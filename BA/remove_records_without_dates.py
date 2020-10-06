from pymarc import MARCReader
import write_error_to_logfile
import ray
from datetime import datetime
import re


def check_record(record):
    try:
        record_id = record['001'].data
        print('checking record:', record_id)
        if record.get_fields('260', '264'):
            if not [date for field in record.get_fields('260', '264') if field['c'] for date in re.findall(r'\d{4}', field['c'])]:
                record.remove_fields('590', '952')
                print(record)
                command = input('Wollen Sie diesen Records löschen? ')
                if command != '':
                    selected_records_by_date_file.write(record.as_marc21())
            else:
                selected_records_by_date_file.write(record.as_marc21())
    except Exception as e:
        write_error_to_logfile.write(e)
    return None


start_evaluation = False



with open('records/selected_records_adjusted_delete_parts_without_proper_title.mrc', 'rb') as selected_record_file:
    with open('records/records_in_date_range.mrc', 'wb') as selected_records_by_date_file:
        try:
            print('starting')
            reader = MARCReader(selected_record_file, force_utf8=True)
            for record in reader:
                check_record(record)

        except Exception as e:
            write_error_to_logfile.write(e)
