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
def check_record(record):
    possible_doublets = []
    try:
        record_id = record['001'].data
        print('checking record:', record_id)
        # if record_id not in doublets:
            # doublets[record_id] = {'doublets': [], 'unrelated': [], 'cases_of_doubt': [],
                                   # 'unconfirmed_non_doublets': [], 'related': []}
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
        with open('records/selected_records_adjusted_delete_parts_without_proper_title.mrc', 'rb') as second_file:
            new_reader = MARCReader(second_file, force_utf8=True)
            for new_record in new_reader:
                if record_id == new_record['001'].data:
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
    except Exception as e:
        write_error_to_logfile.write(e)
    return {record['001'].data: possible_doublets}


start_evaluation = False
starting_record_nr = ''

ray.init(num_cpus=20)
with open('records/selected_records_adjusted_delete_parts_without_proper_title.mrc', 'rb') as selected_record_file:
        try:
            print('starting')
            reader = MARCReader(selected_record_file, force_utf8=True)
            record_list = [record for record in reader]
            for rec_nr in range(0, len(record_list), 20):
                if starting_record_nr in [record_list[i] for i in range(rec_nr, rec_nr + 20)]:
                    start_evaluation = True
                if start_evaluation:
                    now = datetime.now()
                    possible_doublets = [check_record.remote(record_list[i]) for i in range(rec_nr, rec_nr + 20)]
                    possible_doublet_dicts = ray.get(possible_doublets)
                    filename = 'records_checked_' + str(rec_nr)
                    with open(filename, 'w') as file:
                        for doublet_dict in possible_doublet_dicts:
                            file.write(str(doublet_dict) + '\n')

        except Exception as e:
            write_error_to_logfile.write(e)
