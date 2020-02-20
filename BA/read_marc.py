from pymarc import MARCReader

filestring = 'dai01_kexpm101'
count = 0
# out = open('records/hsozkult/hsozkult_to_recent/hsozkult_to_recent' + '_' + str(count) + '.mrc', 'wb')
print(filestring + '.mrc')
with open(filestring, 'rb') as file:
    new_reader = MARCReader(file)
    print(new_reader)
    print()
    for record in new_reader:
        print(record)
        print('quatsch')