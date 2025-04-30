import pandas as pd
import utils as ut
from time import sleep
import json
import requests

input_fol = "input/"

limit = 1

output_fol = "output/csv/"

students = pd.read_excel(f"{input_fol}students.xlsx", sheet_name="Students")
papers_old = pd.read_excel(f"{input_fol}students.xlsx", sheet_name="Papers_backup")
orcids = pd.read_csv(f"{output_fol}orcids_all.csv")
papers_all = pd.read_csv(f"{output_fol}papers_all.csv")
mismatches = pd.read_csv(f"{output_fol}orcid_mismatches.csv")
correct = pd.read_csv(f"{output_fol}orcid_correct.csv")

authors = pd.read_csv(f"{output_fol}old_papers/authors.csv")
mismatched_ids = mismatches["openalex_id"].tolist()
for i, row in authors.iterrows():
    openalex_id = row.openalex_id
    if row.openalex_id in mismatched_ids:
        authors.loc[i, "name_match"] = False

ids_to_check = authors[authors.oxf_aff.isna()]
ids_to_check = ids_to_check["openalex_id"].tolist()
ids_to_check = ids_to_check[:limit]

check = False
if check:
    oxford_url = "https://openalex.org/I40120149"
    for i, row in authors[authors.openalex_id.isin(ids_to_check)].iterrows():
        if i % 10 == 0:
            print(i)
        else:
            pass

        alex_id = row["openalex_id"]
        author_url = f"https://api.openalex.org/authors/{alex_id}"
        response = requests.get(author_url)
        try:
            affs = response.json()["affiliations"]
            affs_list = [aff["institution"]["id"] for aff in affs]
            includes_oxford = oxford_url in affs_list
            if includes_oxford:
                authors.loc[authors.openalex_id == alex_id, "oxf_aff"] = 1
            else:
                authors.loc[authors.openalex_id == alex_id, "oxf_aff"] = 0
        except Exception as e:
            print(e)
            print(alex_id)

        try:
            summary_stats = response.json()["summary_stats"]
            h_index = summary_stats["h_index"]
            i10_index = summary_stats["i10_index"]

            authors.loc[authors.openalex_id == alex_id, "h_index"] = h_index
            authors.loc[authors.openalex_id == alex_id, "i10"] = i10_index
        except Exception as e:
            print(e)

        # pause
        sleep(5)

authors.to_csv(f"{output_fol}authors.csv", index=False)

scrape = True
if scrape:
    # names_already_orcid = list(orcids_ref['name'])
    # names_all = list(students['Name'])

    # names_to_excl = [i for i in names_already_orcid if i not in names_all]
    # # names = [['Ioana','Duta']]
    # # names = ['Ioana Duta']
    # # print(names)

    to_lookup = orcids[~orcids["orcid"].isin(papers_all.orcid)].reset_index(drop=True)

    author_dic = {
        "name": [],
        "orcid": [],
        "ss_id": [],
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
        name = row["name"].strip()
        ORCID = row["orcid"].strip()
        print(name, ORCID)
        # ORCID = ut.get_orcids(name, limit)
        # print(ORCID)
        # orcids_dict['name'].append(name)
        # orcids_dict['orcid'].append(ORCID)

        sleep(5)
        # scrape = ut.orcid_open_alex(ORCID, author_dic, name)
        scrape = ut.get_papers_semantic(name, ORCID)
        with open(f"{output_fol}scrape.json", "w") as f:
            json.dump(scrape, f)
    papers_df = pd.DataFrame(author_dic)
    papers = pd.concat([papers_all, papers_df], ignore_index=True)
    papers.to_csv(f"{output_fol}papers_all.csv", index=False)

papers_new = papers_all[papers_all["orcid"].isin(correct["orcid"])]

# orcids_df = pd.DataFrame(orcids_dict)
# orcids = pd.concat([orcids_ref, orcids_df], ignore_index=True)
# orcids.to_csv(f'{output_fol}orcids.csv', index=False)

# print(set([i.strip() for i in papers_old.Name.dropna() if i not in papers['name_orig']]))
# print(papers_old[~papers_old.Name.isin(papers.name_orig)])
papers_old = papers_old.loc[
    :, ["Name", "DOI", "Title", "Source title", "Year", "Cited by"]
]
papers_old = papers_old.rename(
    columns={
        "Source title": "Journal",
        "Cited by": "Citation Count",
    }
)
papers_new = papers_all.loc[
    :, ["name_orig", "dois", "titles", "journals", "years", "citation_count"]
]
papers_new = papers_new.rename(
    columns={
        "name_orig": "Name",
        "dois": "DOI",
        "titles": "Title",
        "journals": "Journal",
        "years": "Year",
        "citation_count": "Citation Count",
    }
)

papers = pd.concat([papers_new, papers_old], ignore_index=True)
papers = papers.drop_duplicates(subset=["DOI"], keep="first")
correct = correct.loc[:, ['name_orig', 'orcid', 'i10', 'h_index']]
correct = correct.rename(columns={'name_orig': 'Name'})
correct.orcid = 'https://orcid.org/' + correct.orcid.str.strip()
papers = pd.merge(papers, correct, on="Name", how="left")

papers.to_csv(f"{output_fol}papers.csv", index=False)
