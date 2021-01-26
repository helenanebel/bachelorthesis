from nltk import RegexpTokenizer


def is_abbreviation(str1, str2):
    if len(str1) != len(str2):
        abr = min([str1, str2], key=len)
        long = max([str1, str2], key=len)
        if str1[0] == str2[0]:
            long = long[1:]
            for char in abr[1:]:
                found = long.find(char)
                # print(found, long[found])
                long = long[found + 1:]
                if found == -1:
                    return False
    return True


def is_acronym(str1, str2):
    akr = min([str1, str2], key=len)
    long = max([str1, str2], key=len)
    long_list = [token[0] for token in RegexpTokenizer(r'\w+').tokenize(long)]
    long = long[1:]
    for char in akr:
        if char in long_list:
            found = long_list.index(char)
            long = long[found + 1:]
            if found == -1:
                return False
        else:
            return False
    return True
