from pymarc import MARCReader
import write_error_to_logfile
import re
import os

count = 0
with open('records/selected_records_1960.mrc', 'wb') as selected_record_file:
    for filestring in os.listdir('C:/Users/Helena_Nebel/Desktop/Zenon_Daten'):
        with open('C:/Users/Helena_Nebel/Desktop/Zenon_Daten/' + filestring, 'rb') as file:
            try:
                reader = MARCReader(file, force_utf8=True)
                for record in reader:
                    try:
                        if record.get_fields('260', '264'):
                            if [field['c'] for field in record.get_fields('260', '264')]:
                                dates = [re.findall(r'\d{4}', field['c']) for field in record.get_fields('260', '264')
                                         if field['c']]
                                for dates_list in dates:
                                    if any([(1959 < int(year) < 1970) for year in dates_list]):
                                        selected_record_file.write(record.as_marc21())
                                        count += 1
                                    if not dates_list:
                                        print(record['001'], [field['c'] for field in record.get_fields('260', '264')])
                                        selected_record_file.write(record.as_marc21())
                                        count += 1
                            else:
                                selected_record_file.write(record.as_marc21())
                    except Exception as e:
                        print('Error', record['001'])
                        write_error_to_logfile.write(e)
            except Exception as e:
                print('Error', record['001'])
                write_error_to_logfile.write(e)
        print(count)


# gefundene Datensätze in eine einzelne Datei übernehmen.
