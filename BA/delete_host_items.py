from pymarc import MARCReader
import write_error_to_logfile
import json
import os


def delete_upper_host_items():
    with open('upper_host_items_1960.json', 'r') as host_item_file:
        host_item_list = json.load(host_item_file)
    host_items_to_delete = []
    for filestring in os.listdir('C:/Users/Helena_Nebel/Desktop/Zenon_Daten'):
        with open('C:/Users/Helena_Nebel/Desktop/Zenon_Daten/' + filestring, 'rb') as file:
            print(filestring)
            try:
                reader = MARCReader(file, force_utf8=True)
                for record in reader:
                    try:
                        if record['001']:
                            if record['001'].data in host_item_list:
                                record.remove_fields('952', '590', '866', '852')
                                print(record)
                                print('https://zenon.dainst.org/Record/' + record['001'].data)
                                command = input('Möchten Sie alle abhängigen Records löschen? ')
                                if command == 'd':
                                    host_items_to_delete.append(record['001'].data)
                    except Exception as e:
                        print('Error', record['001'])
                        write_error_to_logfile.write(e)
            except Exception as e:
                print('Error', record['001'])
                write_error_to_logfile.write(e)
    with open('host_items_to_delete.json', 'w') as host_item_file:
        json.dump(host_items_to_delete, host_item_file)


def delete_host_items():
    with open('host_items_to_delete.json', 'r') as host_item_file:
        host_item_list = json.load(host_item_file)
    with open('host_items_1960.json', 'r') as item_file:
        item_list = json.load(item_file)
    host_items_to_delete = []
    for filestring in os.listdir('C:/Users/Helena_Nebel/Desktop/Zenon_Daten'):
        with open('C:/Users/Helena_Nebel/Desktop/Zenon_Daten/' + filestring, 'rb') as file:
            print(filestring)
            try:
                reader = MARCReader(file, force_utf8=True)
                for record in reader:
                    try:
                        if record['001']:
                            if (record['001'].data in item_list) and (record['001'].data not in host_item_list):
                                if [field for field in record.get_fields('998') if (field['b'] and field['a'] == 'ANA')]:
                                    for field in record.get_fields('998'):
                                        if field['a'] == 'ANA':
                                            if field['b'] in host_item_list:
                                                if record['001'].data not in host_items_to_delete:
                                                    host_items_to_delete.append(record['001'].data)
                                            else:
                                                record.remove_fields('952', '590', '866', '852')
                                                print(record)
                                                print('https://zenon.dainst.org/Record/' + record['001'].data)
                                                command = input('Möchten Sie alle abhängigen Records löschen? ')
                                                if command == 'd':
                                                    host_items_to_delete.append(record['001'].data)
                                else:
                                    record.remove_fields('952', '590', '866', '852')
                                    print(record)
                                    print('https://zenon.dainst.org/Record/' + record['001'].data)
                                    command = input('Möchten Sie alle abhängigen Records löschen? ')
                                    if command == 'd':
                                        host_items_to_delete.append(record['001'].data)
                    except Exception as e:
                        print('Error', record['001'])
                        write_error_to_logfile.write(e)
            except Exception as e:
                print('Error', record['001'])
                write_error_to_logfile.write(e)
    with open('dependent_host_items_to_delete.json', 'w') as host_item_file:
        json.dump(host_items_to_delete, host_item_file)


def delete_articles_and_volumes():
    with open('dependent_host_items_to_delete.json', 'r') as host_item_file:
        host_item_list = json.load(host_item_file)
    with open('records/selected_records_1960_adjusted.mrc', 'wb') as file_to_write:
        records_processed = 0
        with open('records/selected_records_1960.mrc', 'rb') as file:
            try:
                reader = MARCReader(file, force_utf8=True)
                for record in reader:
                    try:
                        do_write = True
                        if [field for field in record.get_fields('998') if (field['b'] and field['a'] == 'ANA')]:
                            for field in record.get_fields('998'):
                                if field['a'] == 'ANA':
                                    if field['b'] in host_item_list:
                                        do_write = False
                        if do_write:
                            file_to_write.write(record.as_marc21())
                    except Exception as e:
                        write_error_to_logfile.write(e)
            except Exception as e:
                write_error_to_logfile.write(e)


delete_articles_and_volumes()

