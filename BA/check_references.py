import json
from pymarc import MARCReader
import os
import write_error_to_logfile
import copy


def check_record(record, files_to_check, results, stop_evaluation, last_comparison):
    to_delete = []
    last_checked = record['001'].data
    try:
        record_id = record['001'].data
        print('checking record:', record_id)
        record_for_print = copy.deepcopy(record)
        for tag in list(set([field.tag for field in record.get_fields()
                             if field.tag not in ['245', '246', '260', '264', '100']])):
            record_for_print.remove_fields(tag)
        results[record_id] = list(set(results[record_id]))
        print(results[record_id])
        if len(results[record_id]) == 0:
            print(record_for_print)
            last_checked = False
        else:
            if record_id not in doublets:
                doublets[record_id] = []
            notice_new_record = input('Ein neuer Record wird bearbeitet: ')
            start_evaluation = False
            previously_checked = []
            for file in files_to_check:
                with open('records_blocked/' + file, 'rb') as second_file:
                    new_reader = MARCReader(second_file, force_utf8=True)
                    for new_record in new_reader:
                        if new_record['001'].data in previously_checked:
                            continue
                        previously_checked.append(new_record['001'].data)
                        if last_comparison:
                            if new_record['001'].data == last_comparison:
                                start_evaluation = True
                        else:
                            start_evaluation = True
                        if not start_evaluation:
                            continue
                        if record_id == new_record['001'].data:
                            continue
                        elif new_record['001'].data in results[record_id]:
                            new_record_for_print = copy.deepcopy(new_record)
                            for tag in list(set([field.tag for field in new_record.get_fields()
                                                 if field.tag not in ['001', '245', '246', '260', '264']])):
                                new_record_for_print.remove_fields(tag)
                            print()
                            print()
                            print()
                            print('--------------------')
                            print(record_for_print)
                            print('----------')
                            print(new_record_for_print)
                            command_evaluable = False
                            while not command_evaluable:
                                command = input('Sind diese Records Dubletten? ')
                                if command == '':
                                    command_evaluable = True
                                elif command == 'r':
                                    doublets[record_id].append(new_record['001'].data)
                                    command_evaluable = True
                                elif command == 'd':
                                    to_delete.append(new_record['001'].data)
                                    command_evaluable = True
                                elif command == 'e':
                                    stop_evaluation = True
                                    break
                                else:
                                    print('Der eingegebene Befehl ist falsch.')
                        if not stop_evaluation:
                            last_checked = record_id
                            last_comparison = new_record['001'].data
                        else:
                            break
                if stop_evaluation:
                    break
    except Exception as e:
        write_error_to_logfile.write(e)
    return last_checked, last_comparison, stop_evaluation, to_delete

log_file = open('last_checked.json', 'r')
last_checked, last_comparison = json.load(log_file)
stop_evaluation = False
start_evaluation = False

with open('doublets.json', 'r') as doublet_file:
    doublets = json.load(doublet_file)

to_delete_list = []

with open('records_checked.json', 'r') as results_file:
    results = json.load(results_file)
    for record_file_name in os.listdir('records_blocked'):
        if record_file_name == 'records_1968.mrc':
            files_to_check = os.listdir('records_blocked')
        else:
            files_to_check = ['records_1968.mrc']
        with open('records_blocked/' + record_file_name, 'rb') as selected_record_file:
            try:
                print('starting')
                reader = MARCReader(selected_record_file, force_utf8=True)
                record_list = [record for record in reader]
                for record in record_list:
                    if last_checked:
                        if record['001'].data == last_checked:
                            start_evaluation = True
                    else:
                        start_evaluation = True
                    if stop_evaluation:
                        break
                    if start_evaluation:
                        if record['001'].data != last_checked:
                            last_comparison = False
                        last_checked, last_comparison, stop_evaluation, to_delete = \
                            check_record(record, files_to_check, results, stop_evaluation, last_comparison)
                        to_delete_list += to_delete
            except Exception as e:
                write_error_to_logfile.write(e)

with open('doublets.json', 'w') as doublet_file:
    json.dump(doublets, doublet_file)

with open('last_checked.json', 'w') as log_file:
    json.dump([last_checked, last_comparison], log_file)

for item in to_delete_list:
    if item in results:
        del results[item]
    for key in results:
        if item in results[key]:
            results[key].remove(item)

with open('records_checked.json', 'w') as results_file:
    json.dump(results, results_file)
