from pymarc import MARCReader
import write_error_to_logfile
import re

host_item_list = ['000596817', '000046202', '000218929', '000108427', '000218478', '000219930', '000589430',
                  '000590916', '000591921', '000595076', '000596540', '000596817', '000218402', '000218415',
                  '000599514', '000600658', '000218478', '000589430']


def delete_items():
    with open('new_selection', 'wb') as file_to_write:
        with open('records/selected_records_adjusted_delete_parts_without_proper_title.mrc', 'rb') as file:
            try:
                reader = MARCReader(file, force_utf8=True)
                record_nr = 0
                for record in reader:
                    record_nr += 1
                    try:
                        do_write = True
                        if [field for field in record.get_fields('998') if (field['b'] and field['a'] == 'ANA')]:
                            record.remove_fields('952', '590')
                            for field in record.get_fields('998'):
                                if field['a'] == 'ANA':
                                    if field['b'] in host_item_list:
                                        print(record)
                                        command = input('Wollen Sie diesen Record entfernen? ')
                                        if command == '':
                                            do_write = False
                                    elif re.findall(r'\d', record['245']['a']):
                                        print(record)
                                        command = input('Wollen Sie diesen Record entfernen? ')
                                        if command == '':
                                            do_write = False
                                    elif record['245']['n']:
                                        print(record)
                                        command = input('Wollen Sie diesen Record entfernen? ')
                                        if command == '':
                                            do_write = False
                        if do_write:
                            file_to_write.write(record.as_marc21())
                    except Exception as e:
                        write_error_to_logfile.write(e)
            except Exception as e:
                write_error_to_logfile.write(e)


delete_items()

