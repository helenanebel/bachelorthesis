from pymarc import MARCReader
import re
# hier die Records aus records_in_date_range in Blocks aufteilen.

records_missing_date_file = open('records_missing_date.mrc', 'wb')
with open('records/records_in_date_range.mrc', 'rb') as file:
    reader = MARCReader(file, force_utf8=True)
    for record in reader:
        record_dates = [date for field in record.get_fields('260', '264')
                        for field_c in field.get_subfields('c') for date in re.findall(r'\d{4}', field_c)]
        if not record_dates:
            records_missing_date_file.write(record.as_marc21())

for year in range(1960, 1970):
    with open('records_' + str(year) + '.mrc', 'wb') as year_file:
        with open('records/records_in_date_range.mrc', 'rb') as file:
            reader = MARCReader(file, force_utf8=True)
            for record in reader:
                record_dates = [date for field in record.get_fields('260', '264')
                                for field_c in field.get_subfields('c') for date in re.findall(r'\d{4}', field_c)]
                for date in record_dates:
                    if int(date) == year:
                        year_file.write(record.as_marc21())
                        break
