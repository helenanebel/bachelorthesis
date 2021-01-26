

def calc_co_occurence(occurences: list):
    total_coocurrence_count = {}
    occurences_field_1 = list(set([occurence[0] for occurence in occurences]))
    occurences_field_2 = list(set([occurence[1] for occurence in occurences]))
    for occurence in occurences_field_1:
        total_coocurrence_count[occurence] = {}
        for occurence_tuple in occurences:
            if occurence == occurence_tuple[0]:
                if occurence_tuple[1] not in total_coocurrence_count[occurence]:
                    total_coocurrence_count[occurence][occurence_tuple[1]] = 1
                else:
                    total_coocurrence_count[occurence][occurence_tuple[1]] += 1
    total_coocurrence_probability = {occurence_dict_key: {key: total_coocurrence_count[occurence_dict_key][key]/sum(total_coocurrence_count[occurence_dict_key][key]for key in total_coocurrence_count[occurence_dict_key])
                                                          for key in total_coocurrence_count[occurence_dict_key]}
                                     for occurence_dict_key in total_coocurrence_count}
    print('total_prob', total_coocurrence_probability)
occs = [('quatsch', 'grün'), ('quatsch', 'rot'), ('quatsch', 'grün'), ('quatsch', 'blau'),
        ('schwarz', 'rot'), ('schwarz', 'orange'), ('quatsch', 'blau'), ('quatsch', 'grün')]

calc_co_occurence(occs)
# co-occurence sollte dann berücksichtigt werden, wenn sie sehr hoch ist; dann schauen, ob die Worte übereinstimmen.
# verwenden für Verlagsname und Erscheinungsort, falls nur einer davon gegeben ist.

