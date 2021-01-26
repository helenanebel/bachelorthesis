import numpy as np
from weighted_levenshtein import lev, osa, dam_lev
import jaro
import math
import swalign
import pylcs
from difflib import SequenceMatcher
from nltk import RegexpTokenizer

typewriter_layout = [['1','2','3','4','5','6','7','8','9','0'],
                     ['q','w','e','r','t','z','u','i','o','p','u'],
                     ['a','s','d','f','g','h','j','k','l','o', 'a'],
                     ['y','x','c','v','b','n','m'],
                     ]
halfs_of_typewriter = [['1','2','3','4','5','q','w','e','r','t','a','s','d','f','g','y','x','c','v','b'],
                       ['6','7','8','9','0','n','m','z','u','i','o','p', 'h','j','k','l']]


def get_adjacent_chars(typewriter_layout):
    dist_dict = {}
    indentations = [0, 0.5, 1, 1.5]
    for line in typewriter_layout:
        line_idx = typewriter_layout.index(line)
        for char in line:
            dist_dict[char] = []
            char_idx = line.index(char) + indentations[line_idx]
            for second_line in typewriter_layout:
                second_line_idx = typewriter_layout.index(second_line)
                for second_char in second_line:
                    second_char_idx = second_line.index(second_char) + indentations[second_line_idx]
                    char_dist = char_idx - second_char_idx
                    line_dist = line_idx - second_line_idx
                    euclidian_dist = math.sqrt(char_dist**2 + line_dist**2)
                    if euclidian_dist < 1.2:
                        dist_dict[char].append(second_char)
    return dist_dict


# es kann hier wegen der Umlaute zu Problemen kommen; diese werden vorerst vernachlässigt.
# insertcosts so anpassen, dass benachbarte Buchstaben auf der Tastatur grundsätzlich
# beim Insert davor UND danach berücksichtigt werden ist NICHT umsetzbar.
# schauen, ob inserts da sind und diese dann gesondert bewerten!

adjacent_chars = get_adjacent_chars(typewriter_layout)

insert_costs = np.ones(128, dtype=np.float64)

delete_costs = np.ones(128, dtype=np.float64)


substitute_costs = np.ones((128, 128), dtype=np.float64)
for char in adjacent_chars:
    for adjacent_char in adjacent_chars[char]:
        substitute_costs[ord(char), ord(adjacent_char)] = 0.7

transpose_costs = np.ones((128, 128), dtype=np.float64)
for char in halfs_of_typewriter[0]:
    for second_char in halfs_of_typewriter[1]:
        transpose_costs[ord(char), ord(second_char)] = 0.5
        transpose_costs[ord(second_char), ord(char)] = 0.5

# print(osa('BANANA', 'ABNANA', transpose_costs=transpose_costs))

# get distance of Jaro-Winkler to "edit-distance":
print((1-(dam_lev('Nebel', 'Nabel')/max(len('Nebel'), len('Nabel')))) - jaro.jaro_winkler_metric('Nebel', 'Nabel'))
# evtl. noch den Unterschied zwischen Jaro und Jaro-Winkler!

match = 1
mismatch = 0
scoring = swalign.NucleotideScoringMatrix(match, mismatch)

sw = swalign.LocalAlignment(scoring, gap_extension_penalty=0.25, gap_penalty=0)  # you can also choose gap penalties, etc...
alignment = sw.align('Geh besser nicht rein','Geh besser rein')
alignment.dump()
print(alignment.identity) # entspricht normalisierter Levenshtein-Distance.
print(alignment.cigar)
print(alignment.score/21) #[Länge des längeren Strings verwenden]

string1 = "viele leckere würste sind zu haben"
string2 = "zu haben sind viele leckere würste"
iteration_number = 0
print(max(len(RegexpTokenizer(r'\w+').tokenize(string1)), len(RegexpTokenizer(r'\w+').tokenize(string2))))
remaining_size = len(string1)+len(string2)
while True:
    match = SequenceMatcher(None, string1, string2).find_longest_match(0, len(string1), 0, len(string2))
    print(match)  # -> Match(a=0, b=15, size=9)
    if match.size < 3:
        break
    iteration_number += 1
    print(string1[match.a: match.a + match.size])  # -> apple pie
    string1 = string1[:match.a] + string1[match.a+match.size:]
    print(string2[match.b: match.b + match.size])  # -> apple pie
    string2 = string2[:match.b] + string2[match.b+match.size:]
    remaining_size = len(string1) + len(string2)
print(remaining_size)
print(iteration_number)
