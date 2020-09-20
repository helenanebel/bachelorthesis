from pymarc import MARCReader
import write_error_to_logfile
import json
import os


def identify_host_items():
    def get_last_item():
        with open('last_item.json', 'r') as logfile:
            last_item = json.load(logfile)[0]
            return last_item
    with open('host_items_1960.json', 'r') as host_item_file:
        host_item_list = json.load(host_item_file)

    last_item = get_last_item()
    print(last_item)

    with open('selected_records_1960.mrc', 'rb') as original_file:
        try:
            reader = MARCReader(original_file, force_utf8=True)
            start_evaluation = False
            stop_evaluation = False
            for record in reader:
                if stop_evaluation:
                    break
                if last_item:
                    if not start_evaluation:
                        if record['001'].data != last_item:
                            continue
                        else:
                            start_evaluation = True
                            continue
                try:
                    for field in record.get_fields('998'):
                        if field['a'] == 'ANA':
                            if field['b'] not in host_item_list:
                                host_item_list.append(field['b'])
                except Exception as e:
                    print('Error', record['001'])
                    write_error_to_logfile.write(e)
        except Exception as e:
                    print('Error', record['001'])
                    write_error_to_logfile.write(e)

    with open('last_item.json', 'w') as logfile:
        json.dump([last_item], logfile)

    print(len(host_item_list))

    with open('host_items_1960.json', 'w') as host_item_file:
        json.dump(host_item_list, host_item_file)


def identify_upper_host_items():
    with open('host_items_1960.json', 'r') as host_item_file:
        host_item_list = json.load(host_item_file)
    upper_host_item_list = []
    for filestring in os.listdir('C:/Users/Helena_Nebel/Desktop/Zenon_Daten'):
        with open('C:/Users/Helena_Nebel/Desktop/Zenon_Daten/' + filestring, 'rb') as file:
            try:
                reader = MARCReader(file, force_utf8=True)
                for record in reader:
                    try:
                        if record['001'].data in host_item_list:
                            for field in record.get_fields('998'):
                                if field['a'] == 'ANA':
                                    if field['b'] not in upper_host_item_list:
                                        upper_host_item_list.append(field['b'])
                    except Exception as e:
                        print('Error', record['001'])
                        write_error_to_logfile.write(e)
            except Exception as e:
                print('Error', record['001'])
                write_error_to_logfile.write(e)
    with open('upper_host_items_1960.json', 'w') as host_item_file:
        json.dump(upper_host_item_list, host_item_file)


def identify_upper_upper_host_items():
    with open('upper_host_items_1960.json', 'r') as host_item_file:
        upper_host_item_list = json.load(host_item_file)
    upper_upper_host_item_list = []
    for filestring in os.listdir('C:/Users/Helena_Nebel/Desktop/Zenon_Daten'):
        with open('C:/Users/Helena_Nebel/Desktop/Zenon_Daten/' + filestring, 'rb') as file:
            try:
                reader = MARCReader(file, force_utf8=True)
                for record in reader:
                    try:
                        if record['001'].data in upper_host_item_list:
                            for field in record.get_fields('998'):
                                if field['a'] == 'ANA':
                                    if field['b'] not in upper_upper_host_item_list:
                                        upper_upper_host_item_list.append(field['b'])
                    except Exception as e:
                        print('Error', record['001'])
                        write_error_to_logfile.write(e)
            except Exception as e:
                print('Error', record['001'])
                write_error_to_logfile.write(e)
    with open('upper_upper_host_items_1960.json', 'w') as host_item_file:
        json.dump(upper_upper_host_item_list, host_item_file)


identify_upper_upper_host_items()
