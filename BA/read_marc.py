from pymarc import MARCReader
import math
import write_error_to_logfile
from nltk import RegexpTokenizer
import re

typewriter_list = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                   ['q', 'w', 'e', 'r', 't', 'z', 'u', 'i', 'o', 'p', 'ü', '+'],
                   ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'ö', 'ä', '#'],
                   ['y', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '-']]


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


with open('selected_records.mrc', 'wb') as selected_record_file:
    for filestring in ['dai01_kexpm101', 'dai01_kexpm102', 'dai01_kexpm103', 'dai01_kexpm104', 'dai01_kexpm105',
                       'dai01_kexpm106', 'dai01_kexpm107', 'dai01_kexpm108', 'dai01_kexpm109', 'dai01_kexpm110',
                       'dai01_kexpm111']:
        count = 0
        print(filestring)
        with open(filestring, 'rb') as file:
            try:
                reader = MARCReader(file, force_utf8=True)
                for record in reader:
                    try:
                        if [field['c'] for field in record.get_fields('260', '264')]:
                            dates = [re.findall(r'\d{4}', field['c']) for field in record.get_fields('260', '264') if field['c']]
                            for dates_list in dates:
                                if any([(1949 < int(year) < 1986) for year in dates_list]):
                                    print(record)
                                    selected_record_file.write(record.as_marc21())
                                    count += 1
                                if not dates_list:
                                    print(record['001'])
                                    print([field['c'] for field in record.get_fields('260', '264')])
                                    selected_record_file.write(record.as_marc21())
                                    count += 1
                        '''titles = [field['a'] + ' ' + field['b'] if field['b'] else field['a']
                                  for field in record.get_fields('245', '246')]
                        titles_word_lists = [RegexpTokenizer(r'\w+').tokenize(title) for title in titles if title]
                        # print('titles', titles_word_lists)
                        with open(filestring, 'rb') as second_file:
                            new_reader = MARCReader(file)
                            for new_record in new_reader:
                                print(new_record['001'])
                                print([field['c'] for field in new_record.get_fields('260', '264')])
                                titles_for_comparison = [field['a'] + ' ' + field['b']
                                                         if (field['b'] and field['a']) else field['a']
                                                         for field in new_record.get_fields('245', '246')]
                                titles_for_comparison_word_lists = [RegexpTokenizer(r'\w+').tokenize(title)
                                                                    for title in titles_for_comparison if title]
                                # print('comparison_titles', titles_for_comparison_word_lists)'''
                    except Exception as e:
                        print('Error', record['001'])
                        write_error_to_logfile.write(e)
            except Exception as e:
                print('Error', record['001'])
                write_error_to_logfile.write(e)
        print(count)


# gefundene Datensätze in eine einzelne Datei übernehmen. Diese Dateien dann prüfen.
