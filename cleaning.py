import pandas as pd
import utils as ut

inputs = 'input/'
outputs = 'output/'
jsons = f'{outputs}jsons/'
texts = f'{outputs}texts/'

load = True
if load:
    students = pd.read_excel(f'{inputs}students.xlsx', sheet_name='Students')

    print(students.columns)

save_degrees = False
if save_degrees:
    for prefix in ['UG', 'PG']:
        degrees = list(students[f'{prefix}Degree'])

        degrees = list(set(degrees))

        degrees = sorted([str(i) for i in degrees])

        degrees = '\n'.join(degrees)

        ut.save_text_file(f'{prefix}degrees.txt', degrees)

save_unis = False
if save_unis:

    for prefix in ['UG', 'PG']:

        universities = list(students[f'{prefix}University'])

        universities = list(set(universities))

        universities = sorted([str(i) for i in universities])

        universities = '\n'.join(universities)

        ut.save_text_file(f"{prefix}universities.txt", universities)

    # load replacement jsons as dictionary
    ugr = ut.load_json(f'{jsons}UGuniversities_replace.json')
    pgr = ut.load_json(f'{jsons}PGuniversities_replace.json')

    changed_pg = list({pgr[i] for i in pgr.keys() if i != []})
    unchanged_pg = list({i for i in pgr.keys() if i == []})

    changed_ug = list({ugr[i] for i in ugr.keys() if i != []})
    unchanged_ug = list({i for i in ugr.keys() if i == []})

    all_names = changed_pg + unchanged_pg + changed_ug + unchanged_ug
    all_names = sorted(set(all_names))

    ut.save_text_file(f'{texts}all_universities.txt', '\n'.join(all_names))

replace = False
if replace:
    repl = ut.load_json(f'{jsons}universities_replace.json')
    repl = {str(k): v for k, v in repl.items() if v != ""}
    students['PGUniversity_new'] = students['PGUniversity'].replace(repl)
    students['UGUniversity_new'] = students['UGUniversity'].replace(repl)

    students.to_excel('students_replace.xlsx', sheet_name='Students', index=False)

assign_countries = False
if assign_countries:
    # load replacement jsons as dictionary
    countries = ut.load_json(f'{jsons}uni_locations.json')
    students['UGCountry'] = students['UGUniversity'].replace(countries)
    students['PGCountry'] = students['PGUniversity'].replace(countries)
    students.to_excel('students_replace.xlsx', sheet_name='Students', index=False)

assign_categories = True
if assign_categories:
    # load replacement jsons as dictionary
    degrees = ut.load_json(f'{jsons}degrees.json')
    students['UGCategory'] = students['UGDegree'].replace(degrees)
    students['PGCategory'] = students['PGDegree'].replace(degrees)
    students.to_excel('students_replace.xlsx', sheet_name='Students', index=False)

get_degrees = False
if get_degrees:
    pgs = [str(i) for i in students['PGDegree']]
    ugs = [str(i) for i in students['UGDegree']]
    pgs = sorted(list(set(pgs)))
    ugs = sorted(list(set(ugs)))

    ut.save_text_file(f'{texts}PGDegrees.txt', '\n'.join(pgs))
    ut.save_text_file(f'{texts}UGdegrees.txt', '\n'.join(ugs))

ugr = ut.load_json(f'{jsons}UGuniversities_replace.json')
pgr = ut.load_json(f'{jsons}PGuniversities_replace.json')
unis = set(students['UGUniversity']) | set(students['PGUniversity'])

repl = {}
for i in ugr.keys():
    if i not in repl.keys():
        repl[i] = ugr[i]

for i in pgr.keys():
    if i not in repl.keys():
        repl[i] = pgr[i]
