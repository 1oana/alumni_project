import pandas as pd
import json


def save_text_file(filename, data):
    with open(filename, "w") as f:
        f.write(data)
        

def load_json(filename):
    with open(filename) as f:
        return json.load(f)
    

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)


load = True
if load:
    students = pd.read_excel('students.xlsx', sheet_name='Students')

    print(students.columns)
    
save_degrees = False
if save_degrees:
    for prefix in ['UG', 'PG']:
        degrees = list(students[f'{prefix}Degree'])

        degrees = list(set(degrees))

        degrees = sorted([str(i) for i in degrees])

        degrees = '\n'.join(degrees)

        save_text_file(f'{prefix}degrees.txt', degrees)

save_unis = False
if save_unis:

    for prefix in ['UG', 'PG']:

        universities = list(students[f'{prefix}University'])

        universities = list(set(universities))

        universities = sorted([str(i) for i in universities])

        universities = '\n'.join(universities)

        save_text_file(f"{prefix}universities.txt", universities)

    # load replacement jsons as dictionary        
    ugr = load_json('UGuniversities_replace.json')
    pgr = load_json('PGuniversities_replace.json')

    changed_pg = list({pgr[i] for i in pgr.keys() if i != []})
    unchanged_pg = list({i for i in pgr.keys() if i == []})

    changed_ug = list({ugr[i] for i in ugr.keys() if i != []})
    unchanged_ug = list({i for i in ugr.keys() if i == []})

    all_names = changed_pg + unchanged_pg + changed_ug + unchanged_ug
    all_names = sorted(set(all_names))

    save_text_file('all_universities.txt', '\n'.join(all_names))

replace = True
if replace:
    repl = load_json('universities_replace.json')
    repl = {str(k): v for k, v in repl.items() if v != ""}
    students['PGUniversity_new'] = students['PGUniversity'].replace(repl)
    students['UGUniversity_new'] = students['UGUniversity'].replace(repl)

    students.to_excel('students_replace.xlsx', sheet_name='Students', index=False)

assign_countries = True
if assign_countries:
    # load replacement jsons as dictionary        
    countries = load_json('uni_locations.json')
    students['UGCountry'] = students['UGUniversity'].replace(countries)
    students['PGCountry'] = students['PGUniversity'].replace(countries)
    students.to_excel('students_replace.xlsx', sheet_name='Students', index=False)

get_degrees = False
if get_degrees:
    pgs = [str(i) for i in students['PGDegree']]
    ugs = [str(i) for i in students['UGDegree']]
    pgs = sorted(list(set(pgs)))
    ugs = sorted(list(set(ugs)))
 
    save_text_file('PGDegrees.txt', '\n'.join(pgs))
    save_text_file('UGdegrees.txt', '\n'.join(ugs))

ugr = load_json('UGuniversities_replace.json')
pgr = load_json('PGuniversities_replace.json')
unis = set(students['UGUniversity']) | set(students['PGUniversity'])

repl = {}
for i in ugr.keys():
    if i not in repl.keys():
        repl[i] = ugr[i]

for i in pgr.keys():
    if i not in repl.keys():
        repl[i] = pgr[i]
        