from pymarc import MARCReader
import write_error_to_logfile
import re


with open('selected_records.mrc', 'wb') as selected_record_file:
    for filestring in ['dai01_kexpm101', 'dai01_kexpm102', 'dai01_kexpm103', 'dai01_kexpm104', 'dai01_kexpm105',
                       'dai01_kexpm106', 'dai01_kexpm107', 'dai01_kexpm108', 'dai01_kexpm109', 'dai01_kexpm110',
                       'dai01_kexpm111']:
        count = 0
        print(filestring)
        with open(filestring, 'rb') as file:
            try:
                reader = MARCReader(file, force_utf8=True)
                for record in reader:
                    try:
                        if [field['c'] for field in record.get_fields('260', '264')]:
                            dates = [re.findall(r'\d{4}', field['c']) for field in record.get_fields('260', '264') if field['c']]
                            for dates_list in dates:
                                if any([(1979 < int(year) < 1990) for year in dates_list]):
                                    selected_record_file.write(record.as_marc21())
                                    count += 1
                                if not dates_list:
                                    print(record['001'], [field['c'] for field in record.get_fields('260', '264')])
                                    selected_record_file.write(record.as_marc21())
                                    count += 1
                    except Exception as e:
                        print('Error', record['001'])
                        write_error_to_logfile.write(e)
            except Exception as e:
                print('Error', record['001'])
                write_error_to_logfile.write(e)
        print(count)


# gefundene Datensätze in eine einzelne Datei übernehmen.
