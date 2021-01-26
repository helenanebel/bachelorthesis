import fuzzy
import cologne_phonetics
import urllib.request
import json

soundex = fuzzy.Soundex(4)
print(soundex('fuzzy'))
dmeta = fuzzy.DMetaphone()
print(dmeta('chmiet'))
print(dmeta('schmid'))
print(fuzzy.nysiis('fuzzy'))
print(cologne_phonetics.encode("Kraut"))
print(cologne_phonetics.encode("Schmid"))

first_name = 'R*'  # Initialen mit Wildcard beenden!
last_name = 'Koch'
with urllib.request.urlopen("https://lobid.org/gnd/search?q=(preferredName%3A"
                            + first_name + "+OR+variantName%3A" + first_name + ")"
                            "+AND+(preferredName%3A" + last_name + "+OR+variantName%3A" + last_name + ")"
                            "&filter=type%3ADifferentiatedPerson&from=0&size=100&format=json") as url:
    data = json.loads(url.read().decode())
    for item in data['member']:
        print(item['preferredName'], item['variantName'])
# hieraus sollte dann noch ein Thesaurus gebastelt werden...
