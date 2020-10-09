from pymarc import MARCReader
import os
import write_error_to_logfile
from nltk import RegexpTokenizer
from nltk.corpus import stopwords
import unidecode
from langdetect import detect
import ray
from datetime import datetime
import re
import json

stopwords_dict = {'de': stopwords.words('german'), 'en': stopwords.words('english'), 'fr': stopwords.words('french'),
                  'es': stopwords.words('spanish'), 'it': stopwords.words('italian'), 'nl': stopwords.words('dutch')}


def lower_list(input_list):
    output_list = [word.lower() for word in input_list]
    return output_list


def iterative_levenshtein(s, t):
    try:
        s, t = [string.lower() for string in [s, t]]
        rows = len(s) + 1
        cols = len(t) + 1
        deletes, inserts, substitutes = 1, 1, 1
        dist = [[0.0 for x in range(cols)] for x in range(rows)]
        for row in range(1, rows):
            dist[row][0] = row * deletes
        for col in range(1, cols):
            dist[0][col] = col * inserts
        for col in range(1, cols):
            for row in range(1, rows):
                dist[row][col] = min(dist[row - 1][col] + deletes,
                                     dist[row][col - 1] + inserts,
                                     dist[row - 1][col - 1] + 1)
        return dist[len(s)][len(t)]
    except Exception as e:
        write_error_to_logfile.write(e)


@ray.remote
def check_record(record):
    possible_doublets = []
    try:
        record_id = record['001'].data
        print('checking record:', record_id)
        title = [field['a'] if field['a'] else '' for field in record.get_fields('245')][0] if record.get_fields('245') else ''
        try:
            language = detect(title)
        except:
            language = 'xx'
        title = unidecode.unidecode(title)
        title_word_list = lower_list([word for word in RegexpTokenizer(r'\w+').tokenize(title) if len(word) > 1])
        title_word_list = [word for word in title_word_list
                              if word not in (stopwords_dict[language] if
                                              language in stopwords_dict else [])][:7]
        with open('records/records_in_date_range.mrc', 'rb') as second_file:
            new_reader = MARCReader(second_file, force_utf8=True)
            for new_record in new_reader:
                if record_id == new_record['001'].data:
                    continue
                titles_for_comparison = [field['a'] + ' ' + field['b']
                                             if (field['b'] and field['a']) else field['a']
                                             for field in new_record.get_fields('245', '246')]
                for title_for_comparison in titles_for_comparison:
                    if title_for_comparison:
                        try:
                            language = detect(title)
                        except:
                            language = 'xx'
                        title_for_comparison = unidecode.unidecode(title_for_comparison)
                        title_for_comparison_word_list = lower_list([word for word
                                                             in RegexpTokenizer(r'\w+').tokenize(title_for_comparison)
                                                             if len(word) > 1])
                        title_for_comparison_word_list = [word for word
                                                          in title_for_comparison_word_list
                                                          if word not in (stopwords_dict[language]
                                                                          if language in stopwords_dict else [])]
                        found_words = 0
                        for word in title_word_list:
                            for word_for_comparison in title_for_comparison_word_list:
                                if iterative_levenshtein(word, word_for_comparison) <= (len(word) / 3):
                                    found_words += 1
                        if found_words >= int(len(title_word_list) / 2):
                            possible_doublets.append(new_record['001'].data)
                            break
    except Exception as e:
        write_error_to_logfile.write(e)
        possible_doublets.append('problem')
    return {record['001'].data: possible_doublets}


start_evaluation = True
# starting_record_nr = 'AR011026178'

ray.init(num_cpus=15)
for record_file_name in os.listdir('records_blocked'):
    if re.findall(r'\d{4}', record_file_name):
        date = re.findall(r'\d{4}', record_file_name)[0]
        files_to_check = ['records_' + str(year) + '.mrc'
                          for year in range(int(date) - 1, int(date) + 2) if (1959 < year < 1970)] \
                         + ['records_missing_date.mrc']
    else:
        files_to_check = os.listdir('records_blocked')
    for file in files_to_check:
        with open('records_blocked/' + file, 'rb') as selected_record_file:
            try:
                print('starting')
                reader = MARCReader(selected_record_file, force_utf8=True)
                record_list = [record for record in reader]
                for rec_nr in range(0, len(record_list), 15):
                    # if starting_record_nr in [record_list[i]['001'].data for i in range(rec_nr, rec_nr + 15)]:
                        # start_evaluation = True
                    if start_evaluation:
                        now = datetime.now()
                        possible_doublets = [check_record.remote(record_list[i]) for i in range(rec_nr, rec_nr + 15)]
                        possible_doublet_dicts = ray.get(possible_doublets)
                        for doublet_dict in possible_doublet_dicts:
                            filename = 'records_checked_' + str(rec_nr)
                            with open(filename, 'w') as file:
                                file.write(str(doublet_dict) + '\n')
            except Exception as e:
                write_error_to_logfile.write(e)

# neues Vorgehen mit reduzierter Listenlänge ab 000106797
# Vorgehen mit Problemdokumentation & Error-handling ab AR011026178 (auf dem remote-Rechner)
# neuer Start mit geblockten Records & angepasstem Levensthein & anderem Vorgehen bei Language-Vergleich
# (nicht den Titel des ursprungsrecords verwenden für language detection, sondern jeweils den eigenen Titel.)
# Abgleich mit bereits geprüften Records einführen, um die Zeit zu verringern.
# pre-check-records anpassen, sodass jeweils ein file nur mit vier anderen verglichen werden muss.