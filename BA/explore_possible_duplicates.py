from pymarc import MARCReader
import unidecode
from nltk.tokenize import RegexpTokenizer
import re
from scipy import spatial
import os
import sys


def lower_list(input_list):
    output_list = [word.lower() for word in input_list]
    return output_list


def check_cosine_similarity(title, found_title):
    try:
        found_title = unidecode.unidecode(found_title)
        title = unidecode.unidecode(title)
        title_list = RegexpTokenizer(r'\w+').tokenize(title)
        found_title_list = RegexpTokenizer(r'\w+').tokenize(found_title)
        [title_list, found_title_list] = [lower_list(a) for a in [title_list, found_title_list]]
        title_list = [word for word in title_list if
                      ((re.findall(r'^\d{1,2}$', word) == []) and (re.findall(r'^[ivxlcdm]*$', word) == []))]
        found_title_list = [word for word in found_title_list if
                            ((re.findall(r'^\d{1,2}$', word) == []) and (re.findall(r'^[ivxlcdm]*$', word) == []))]
        [title_list, found_title_list] = [lower_list(a) for a in [title_list, found_title_list]]
        length = min(len(title_list), len(found_title_list))
        # Längenvergleich der Titel sollte stattfinden!!!
        [title_list, found_title_list] = [a[:length] for a in [title_list, found_title_list]]
        title_list_count = [title_list.count(word) for word in title_list]
        found_title_list_count = [found_title_list.count(word) for word in title_list]
        if list(set(title_list_count)) == [0] or list(set(found_title_list_count)) == [0]:
            return False
        else:
            similarity = 1 - spatial.distance.cosine(title_list_count, found_title_list_count)
            if similarity <= 0.65:
                return True
        return False
    except Exception as e:
        print('Error! Code: {c}, Message, {m}'.format(c=type(e).__name__, m=str(e)))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


filestring = 'dai01_kexpm101'
count = 0
# out = open('records/hsozkult/hsozkult_to_recent/hsozkult_to_recent' + '_' + str(count) + '.mrc', 'wb')
print(filestring + '.mrc')
with open(filestring, 'rb') as file:
    new_reader = MARCReader(file)
    for record in new_reader:
        if '245' in record:
            print(record['245'])
# alle Dateien in ein MARC-File packen und dann mögliche Dubletten (Kosinus-Similarität > 0.4) händisch überprüfen.
# Für wie viele MARC-Datensätze soll das geschehen?
