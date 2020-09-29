from pymarc import MARCReader
import math
import write_error_to_logfile
from nltk import RegexpTokenizer
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import json
import unidecode
from langdetect import detect
import ray
from datetime import datetime
import os

stopwords_dict = {'de': stopwords.words('german'), 'en': stopwords.words('english'), 'fr': stopwords.words('french'),
                  'es': stopwords.words('spanish'), 'it': stopwords.words('italian'), 'nl': stopwords.words('dutch')}


typewriter_list = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                   ['q', 'w', 'e', 'r', 't', 'z', 'u', 'i', 'o', 'p', 'ü', '+'],
                   ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'ö', 'ä', '#'],
                   ['y', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '-']]


def lower_list(input_list):
    output_list = [word.lower() for word in input_list]
    return output_list


def typewriter_distance(letter1, letter2):
    try:
        typewriter_position = [(typewriter_list.index(row), row.index(letter))
                               if (typewriter_list.index(row) != 2)
                               else (typewriter_list.index(row), row.index(letter) + 0.5)
                               for letter in [letter1, letter2]
                               for row in typewriter_list if (letter in row)]
        try:
            distance = math.sqrt((abs(typewriter_position[0][0] - typewriter_position[1][0])) ** 2 + (
                abs(typewriter_position[0][1] - typewriter_position[1][1])) ** 2)
        except:
            distance = 1
        return distance
    except Exception as e:
        write_error_to_logfile.write(e)


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
                                     dist[row - 1][col - 1] + typewriter_distance(s[row - 1], t[col - 1]))
        return dist[len(s)][len(t)]
    except Exception as e:
        write_error_to_logfile.write(e)


@ray.remote
def check_record(record, filename):
    possible_doublets = []
    try:
        record_id = record['001'].data
        print('checking record:', record_id)
        if record_id not in doublets:
            doublets[record_id] = {'doublets': [], 'unrelated': [], 'cases_of_doubt': [],
                                   'unconfirmed_non_doublets': [], 'related': []}
        titles = [field['a'] if field['a'] else '' for field in record.get_fields('245', '246')][:6]
        languages = [detect(title) for title in titles]
        titles = [unidecode.unidecode(title) for title in titles if title]
        titles_word_lists = [[word for word
                              in RegexpTokenizer(r'\w+').tokenize(title) if len(word) > 1]
                             for title in titles if title]
        titles_word_lists = [lower_list(word_list) for word_list in titles_word_lists]
        titles_word_lists = [[word for word in word_list
                              if word not in (stopwords_dict[languages[titles_word_lists.index(word_list)]] if
                                              languages[titles_word_lists.index(word_list)] in stopwords_dict else [])]
                             for word_list in titles_word_lists]
        with open('selected_records_adjusted_delete_parts_without_proper_title.mrc', 'rb') as second_file:
            new_reader = MARCReader(second_file, force_utf8=True)
            for new_record in new_reader:
                if record_id == new_record['001'].data:
                    continue
                if new_record['001'].data in doublets:
                    if record_id not in doublets[new_record['001'].data]['unconfirmed_non_doublets']:
                        continue
                titles_for_comparison = [field['a'] + ' ' + field['b']
                                         if (field['b'] and field['a']) else field['a']
                                         for field in new_record.get_fields('245', '246')]
                titles_for_comparison = [unidecode.unidecode(title) for title in titles_for_comparison if title]
                titles_for_comparison_word_lists = [[word for word
                                                     in RegexpTokenizer(r'\w+').tokenize(title)
                                                     if len(word) > 1]
                                                    for title in titles_for_comparison if title]

                titles_for_comparison_word_lists = [lower_list(word_list) for word_list in
                                                    titles_for_comparison_word_lists]

                title_nr = 0
                for title_word_list in titles_word_lists:
                    language = languages[title_nr]
                    for title_for_comparison_word_list in titles_for_comparison_word_lists:
                        title_for_comparison_word_list = [word for word
                                                          in title_for_comparison_word_list
                                                          if word not in (stopwords_dict[language]
                                                                          if language in stopwords_dict else [])]
                        found_words = 0
                        for word in title_word_list:
                            for word_for_comparison in title_for_comparison_word_list:
                                if iterative_levenshtein(word, word_for_comparison) <= len(word) / 3:
                                    found_words += 1
                        title_nr += 1
                        if found_words >= len(title_word_list) / 2:
                            possible_doublets.append(new_record['001'].data)
        with open(filename, 'a+') as file:
            file.write({record['001'].data: possible_doublets})
    except Exception as e:
        write_error_to_logfile.write(e)
    return possible_doublets


log_file = open('last_checked.json', 'r')
last_checked, last_comparison = json.load(log_file)
stop_evaluation = False


ray.init(num_cpus=8)
with open('selected_records_adjusted_delete_parts_without_proper_title.mrc', 'rb') as selected_record_file:
    with open('doublets.json', 'r') as doublet_file:
        doublets = json.load(doublet_file)
        try:
            reader = MARCReader(selected_record_file, force_utf8=True)
            record_list = [record for record in reader]
            for rec_nr in range(0, len(record_list), 10): # Dateipfad: '/content/drive/My Drive/
                now = datetime.now()
                filename = 'records_checked_' + str(rec_nr)
                file = open(filename, 'w')
                file.close()
                possible_doublets = [check_record.remote(record_list[i], file) for i in range(rec_nr, rec_nr + 10)]
                possible_doublets = ray.get(possible_doublets)
                print(possible_doublets)
                if rec_nr % 100 == 0:
                    complete_file = 'records_checked_complete_' + str(rec_nr)
                    with open(complete_file, 'w') as file:
                        for record_file in os.listdir(''):
                            if 'complete' not in record_file:
                                if int(record_file.replace('records_checked_', '')) > rec_nr - 100:
                                    with open(record_file, 'r') as readfile:
                                        to_write = readfile.read()
                                        file.write(to_write)

        except Exception as e:
            write_error_to_logfile.write(e)
