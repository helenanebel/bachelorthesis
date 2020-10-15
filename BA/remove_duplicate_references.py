import json
import os


with open('records_checked.json', 'w') as results_file:
    results = {}
    for filename in os.listdir('records_checked'):
        with open('records_checked/' + filename, 'r') as file:
            result_list = file.read()
            for line in result_list.split('\n')[:-1]:
                line = line.replace("'", '"')
                dict = json.loads(line)
                key = list(dict.keys())[0]
                if key not in results:
                    results[key] = []
                    for found_id in dict[key]:
                        if found_id not in results:
                            results[key].append(found_id)
                        else:
                            if key in results[found_id]:
                                continue
                            else:
                                results[key].append(found_id)
    json.dump(results, results_file)
