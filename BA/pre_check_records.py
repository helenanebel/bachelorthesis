from pymarc import MARCReader
import os
import write_error_to_logfile
from nltk import RegexpTokenizer
from nltk.corpus import stopwords
import unidecode
from langdetect import detect
import ray
import math
import re
import json

stopwords_dict = {'de': stopwords.words('german'), 'en': stopwords.words('english'), 'fr': stopwords.words('french'),
                  'es': stopwords.words('spanish'), 'it': stopwords.words('italian'), 'nl': stopwords.words('dutch')}

with open('stopword_languages.json', 'r') as languages_file:
    languages_dict = json.load(languages_file)


def lower_list(input_list):
    output_list = [word.lower() for word in input_list]
    return output_list


def iterative_levenshtein(s, t, costs=(1, 1, 1)):
    try:
        """
        iterative_levenshtein(s, t) -> ldist
        ldist is the Levenshtein distance between the strings
        s and t.
        For all i and j, dist[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t

        costs: a tuple or a list with three integers (d, i, s)
               where d defines the costs for a deletion
                     i defines the costs for an insertion and
                     s defines the costs for a substitution
        """
        # https://www.python-course.eu/levenshtein_distance.php
        rows = len(s) + 1
        cols = len(t) + 1
        deletes, inserts, substitutes = costs

        dist = [[0 for x in range(cols)] for x in range(rows)]

        # source prefixes can be transformed into empty strings
        # by deletions:
        for row in range(1, rows):
            dist[row][0] = row * deletes

        # target prefixes can be created from an empty source string
        # by inserting the characters
        for col in range(1, cols):
            dist[0][col] = col * inserts

        for col in range(1, cols):
            for row in range(1, rows):
                if s[row - 1] == t[col - 1]:
                    cost = 0
                else:
                    cost = substitutes
                dist[row][col] = min(dist[row - 1][col] + deletes,
                                     dist[row][col - 1] + inserts,
                                     dist[row - 1][col - 1] + cost)  # substitution

        return dist[row][col]
    except Exception as e:
        write_error_to_logfile.write(e)
        return 0


@ray.remote
def check_record(record, files_to_check):
    possible_doublets = []
    try:
        subfield_p = False
        record_id = record['001'].data
        title = [field['a'] if field['a'] else '' for field in record.get_fields('245')][0] if record.get_fields('245') else ''
        title_for_language_detection = [field['a'] + ' ' + field['b'] if (field['a'] and field['b']) else field['a'] if field['a'] else '' for field in record.get_fields('245')][0] if record.get_fields('245') else ''
        try:
            if record_id in languages_dict:
                language = languages_dict[record_id]
            else:
                language = detect(title_for_language_detection)
        except:
            language = 'xx'
        if record.get_fields('245'):
            if record['245']['p']:
                subfield_p = True
        title = unidecode.unidecode(title)
        title = title.lower()
        title = title.replace(' al-', ' ')
        words_with_hyphen = re.findall(r'[a-z]+[-][a-z]+', title)
        print(words_with_hyphen)
        title = title.split(". - ")[0].split(".- ")[0].split(" / ")[0]
        title_word_list = [word for word in RegexpTokenizer(r'\w+').tokenize(title) if len(word) > 1]
        title_word_list = [word for word in title_word_list
                              if word not in (stopwords_dict[language] if
                                              language in stopwords_dict else [])][:7] + words_with_hyphen
        for file in files_to_check:
            # print(file)
            with open('records_blocked/' + file, 'rb') as second_file:
                new_reader = MARCReader(second_file, force_utf8=True)
                for new_record in new_reader:
                    if record_id == new_record['001'].data:
                        continue
                    titles_for_comparison = [field['a'] + ' ' + field['b'] + ' ' + field['p']
                                             if (field['b'] and field['a'] and field['p'] and subfield_p)
                                             else field['a'] + ' ' + field['b'] if (field['b'] and field['a'])
                                             else field['a'] + ' ' + field['p']
                                             if (field['p'] and field['a'] and subfield_p)
                                             else field['a'] for field in new_record.get_fields('245', '246')]
                    for title_for_comparison in titles_for_comparison:
                        if title_for_comparison:
                            title_for_comparison = unidecode.unidecode(title_for_comparison)
                            title_for_comparison_word_list = lower_list([word for word
                                                                 in RegexpTokenizer(r'\w+').tokenize(title_for_comparison)
                                                                 if len(word) > 1])
                            title_for_comparison_word_list = [word for word in title_for_comparison_word_list
                                                              if word not in (stopwords_dict[language] if
                                                                              language in stopwords_dict else [])][:10]
                            found_words = 0
                            sufficient_word_number = math.ceil(len(title_word_list) / 2)
                            if len(title_word_list) == 2:
                                sufficient_word_number = 2
                            for word in title_word_list:
                                if found_words == sufficient_word_number:
                                    break
                                for word_for_comparison in title_for_comparison_word_list:
                                    if len(title_word_list) in [1, 2]:
                                        if iterative_levenshtein(word, word_for_comparison) <= (len(word) / 2.5):
                                            found_words += 1
                                            break
                                    else:
                                        if iterative_levenshtein(word, word_for_comparison) <= (len(word) / 3):
                                            found_words += 1
                                            break
                            if found_words >= sufficient_word_number:
                                possible_doublets.append(new_record['001'].data)
                                break
    except Exception as e:
        write_error_to_logfile.write(e)
        possible_doublets.append('problem')
    return {record['001'].data: possible_doublets}


start_evaluation = True
# starting_record_nr = 'AR011026178'

ray.init(num_cpus=18)
for record_file_name in os.listdir('records_blocked'):
    print(record_file_name)
    if record_file_name == "records_1968.mrc":
        files_to_check = os.listdir('records_blocked')
    else:
        files_to_check = ["records_1968.mrc"]
    with open('records_blocked/' + record_file_name, 'rb') as selected_record_file:
        try:
            print('starting')
            reader = MARCReader(selected_record_file, force_utf8=True)
            record_list = [record for record in reader]
            for rec_nr in range(0, len(record_list), 18):
                if start_evaluation:
                    if (rec_nr + 17) >= (len(record_list)):
                        possible_doublets = [check_record.remote(record_list[i], files_to_check) for i in
                                             range(rec_nr, len(record_list))]
                        possible_doublet_dicts = ray.get(possible_doublets)
                        record_file_name = record_file_name.replace('.mrc', '')
                        filename = record_file_name + '_' + str(rec_nr)
                        with open(filename, 'w') as file:
                            for doublet_dict in possible_doublet_dicts:
                                file.write(str(doublet_dict) + '\n')
                    else:
                        possible_doublets = [check_record.remote(record_list[i], files_to_check)
                        for i in range(rec_nr, rec_nr + 18)]
                        possible_doublet_dicts = ray.get(possible_doublets)
                        record_file_name = record_file_name.replace('.mrc', '')
                        filename = record_file_name + '_' + str(rec_nr)
                        with open(filename, 'w') as file:
                            for doublet_dict in possible_doublet_dicts:
                                file.write(str(doublet_dict) + '\n')
        except Exception as e:
            write_error_to_logfile.write(e)
            print(e)
