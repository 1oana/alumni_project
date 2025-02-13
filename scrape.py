import pandas as pd
import utils as ut
from time import sleep
import json
import requests

input_fol = "input/"

limit = 0

output_fol = "output/csv/"

students = pd.read_excel(f'{input_fol}students.xlsx', sheet_name='Students')
orcids = pd.read_csv(f'{output_fol}orcids.csv')
papers_all = pd.read_csv(f'{output_fol}papers_all.csv')
mismatches = pd.read_csv(f'{output_fol}orcid_mismatches.csv')

authors = pd.read_csv(f'{output_fol}authors.csv')
mismatched_ids = mismatches['openalex_id'].tolist()
for i, row in authors.iterrows():
    openalex_id = row.openalex_id
    if row.openalex_id in mismatched_ids:
        print(row.name_orig)
        authors.loc[i, 'name_match'] = False

ids_to_check = authors[authors.oxf_aff.isna()]
ids_to_check = ids_to_check['openalex_id'].tolist()
ids_to_check = ids_to_check[:limit]

check = False
if check:
    oxford_url = "https://openalex.org/I40120149"
    for i, row in authors[authors.openalex_id.isin(ids_to_check)].iterrows():
        if i % 10 == 0:
            print(i)
        else:
            pass

        alex_id = row['openalex_id']
        author_url = f"https://api.openalex.org/authors/{alex_id}"
        response = requests.get(author_url)
        try:
            affs = response.json()['affiliations']
            affs_list = [aff['institution']['id'] for aff in affs]
            includes_oxford = oxford_url in affs_list
            if includes_oxford:
                authors.loc[authors.openalex_id == alex_id, 'oxf_aff'] = 1
            else:
                authors.loc[authors.openalex_id == alex_id, 'oxf_aff'] = 0
        except Exception as e:
            print(e)
            print(alex_id)

        try:
            summary_stats = response.json()['summary_stats']
            h_index = summary_stats['h_index']
            i10_index = summary_stats['i10_index']

            authors.loc[authors.openalex_id == alex_id, 'h_index'] = h_index
            authors.loc[authors.openalex_id == alex_id, 'i10'] = i10_index
        except Exception as e:
            print(e)

        # pause
        sleep(5)

authors.to_csv(f'{output_fol}authors.csv', index=False)

scrape = False
if scrape:

    # names_already_orcid = list(orcids_ref['name'])
    # names_all = list(students['Name'])

    # names_to_excl = [i for i in names_already_orcid if i not in names_all]
    # # names = [['Ioana','Duta']]
    # # names = ['Ioana Duta']
    # # print(names)

    to_lookup = orcids[~orcids['orcid'].isin(papers_all.orcid)].reset_index(drop=True)

    author_dic = {
        "name": [],
        "orcid": [],
        "openalex_id": [],
        "dois": [],
        "titles": [],
        "journals": [],
        "years": [],
        "citation_count": [],
    }

    for i, row in to_lookup.iterrows():
        if i >= limit:
            break
        else:
            pass
        name = row['name'].strip()
        ORCID = row['orcid'].strip()
        print(name, ORCID)
        # ORCID = ut.get_orcids(name, limit)
        # print(ORCID)
        # orcids_dict['name'].append(name)
        # orcids_dict['orcid'].append(ORCID)

        sleep(5)
        scrape = ut.orcid_open_alex(ORCID, author_dic, name)
        with open(f'{output_fol}scrape.json', 'w') as f:
            json.dump(scrape, f)
    papers_df = pd.DataFrame(author_dic)
    papers = pd.concat([papers_all, papers_df], ignore_index=True)
    papers.to_csv(f'{output_fol}papers.csv', index=False)

papers = papers_all[~papers_all['orcid'].isin(mismatches['orcid'])]
papers.to_csv('output/papers.csv', index=False)

# orcids_df = pd.DataFrame(orcids_dict)
# orcids = pd.concat([orcids_ref, orcids_df], ignore_index=True)
# orcids.to_csv(f'{output_fol}orcids.csv', index=False)
