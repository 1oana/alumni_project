import pandas as pd
import utils as ut
from time import sleep
import json
import requests
import details as dt

input_fol = "input/"

limit = 1

output_fol = "output/csv/"

students = pd.read_excel(dt.STUDENTS_EXCEL_NAME, sheet_name=dt.STUDENTS_SHEET_NAME)
papers_old = pd.read_excel(dt.STUDENTS_EXCEL_NAME, sheet_name=dt.OLD_PAPERS_SHEET_NAME)
# orcids = pd.read_csv(f"{output_fol}orcids_all.csv")
papers_all = pd.read_csv(f"{output_fol}papers_all.csv")
correct = pd.read_csv(f"{output_fol}orcid_correct.csv")
authors = pd.read_csv(f"{output_fol}old_papers/authors.csv")


oxford_url = "https://openalex.org/I40120149"


def get_orcids(name, limit):
    """
    Searches ORCID database for a certain name.
    Returns top OCID match if one is found to match the name.

    Parameters
    ----------

    name : str
        The name of the author to search for.
    limit : int
        The maximum number of results to return in the ORCID search.

    Returns
    -------
    str or None
        The best match ORCID ID if one is found, otherwise None.


    """
    url = f"https://pub.orcid.org/v3.0/search/?q={name}&rows={limit}"
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        results = data.get("result", [])

        if results:
            person = results[0]
            orcid_id = person["orcid-identifier"]["path"]
            print(f"ORCID: https://orcid.org/{orcid_id}")
            return orcid_id
        else:
            print("No ORCID ID found for this name.")
            return None
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None


def save_json(data, filename):
    """
    Save data to a JSON file.

    Parameters
    ----------

    data : dict
        The data to save.
    filename : str
        The name of the file to save the data to.

    Returns
    -------
    None
    """
    with open(filename, "w") as f:
        json.dump(data, f)


def save_csv(data, filename):
    """
    Save data to a CSV file.

    Parameters
    ----------

    data : DataFrame
        The data to save.
    filename : str
        The name of the file to save the data to.

    Returns
    -------
    None
    """
    data.to_csv(filename, index=False)


def save_papers(author_dic, papers_all, output_fol):
    papers_df = pd.DataFrame(author_dic)
    papers = pd.concat([papers_all, papers_df], ignore_index=True)
    papers.to_csv(f"{output_fol}papers_all.csv", index=False)


def orcid_open_alex(ORCID):
    """
    Look up an ORCID on OpenAlex.
    Retrieve the OpenAlex profile and print the author's information.

    Parameters
    ----------

    ORCID : str
        The ORCID identifier of the author.

    Returns
    -------

    None
    """

    # Search author
    orcid_text = f"https://orcid.org/{ORCID}"
    author_url = f"https://api.openalex.org/authors/{orcid_text}"
    print(author_url)
    response = requests.get(author_url)

    if response.status_code == 200:
        author_data = response.json()
        print(author_data)
        if author_data:
            print("Author found.")
            author_id = author_data["id"]
            return author_id
        else:
            print("Author not found.")
            return "Error"
    else:
        print(f"Error {response.status_code}: {response.text}")
        return "Error"


def lookup_open_alex(ORCID, author_dic, name_given, openalex_id=None):
    """
    Look up an ORCID on OpenAlex.
    Retrieve the OpenAlex profile and populate author_dic with the author's information.

    Parameters
    ----------

    ORCID : str
        The ORCID identifier of the author.
    author_dic : dict
        A dictionary to store author information.
    name_given : str
        The name of the author.
    aff : str, optional
        The affiliation to filter papers by (default is "University of Oxford").

    Returns
    -------

    dict
        The updated author_dic with the author's information.
    """

    if openalex_id is None:
        # Search author
        openalex_id = orcid_open_alex(ORCID)
    else:
        pass

    if openalex_id != "Error":
        papers_url = f"https://api.openalex.org/works?filter=author.id:{openalex_id}"
        papers_response = requests.get(papers_url)
        papers = papers_response.json()["results"]

        print("- Fetching author data...")
        author_response = requests.get(
            f"https://api.openalex.org/authors/{openalex_id}"
        )

        summary_stats = author_response.json()["summary_stats"]
        h_index = summary_stats["h_index"]
        i10_index = summary_stats["i10_index"]

        for paper in papers:
            try:
                # get journal-level metrics
                journal = paper["primary_location"]["source"]["display_name"]
                journal_id = paper["primary_location"]["source"]["id"]

                journal_id_url = f"https://api.openalex.org/sources/{journal_id}"
                # look up on api
                journal_call = requests.get(journal_id_url)
                journal_object = journal_call.json()

                # get journal metrics
                journal_metrics = journal_object["summary_stats"]
                twoyr_mc = journal_metrics["2yr_mean_citedness"]
                journal_i10 = journal_metrics["i10_index"]
                journal_h_index = journal_metrics["h_index"]

            except TypeError as e:
                print(paper['id'])
                journal = "Unknown"
                if paper["primary_location"] is None:
                    journal_id = "Unknown"
                else:
                    journal_id = paper["primary_location"]["landing_page_url"]
                twoyr_mc = "Unknown"
                journal_i10 = "Unknown"
                journal_h_index = "Unknown"
                print(f"Error retrieving journal information: {e}")

            author_dic["dois"].append(paper["doi"])
            author_dic["name"].append(name_given)
            author_dic["orcid"].append(ORCID)
            author_dic["openalex_id"].append(openalex_id)
            author_dic["titles"].append(paper["title"])
            author_dic["journals"].append(journal)
            author_dic["years"].append(paper["publication_year"])
            author_dic["citation_count"].append(paper["cited_by_count"])
            author_dic["h_index"].append(h_index)
            author_dic["i10"].append(i10_index)
            author_dic["work_id"].append(paper["id"])
            # add journal-level metrics
            author_dic["two_year_mc"].append(twoyr_mc)
            author_dic["journal_h_index"].append(journal_h_index)
            author_dic["journal_i10"].append(journal_i10)
            author_dic["journal_id"].append(journal_id)

    else:
        print("Author not found.")
        author_dic["name"].append(name_given)
        author_dic["orcid"].append(ORCID)
        author_dic["openalex_id"].append("Error")
        author_dic["titles"].append("Error")
        author_dic["journals"].append("Error")
        author_dic["years"].append("Error")
        author_dic["citation_count"].append("Error")
        author_dic["h_index"].append("Error")
        author_dic["i10"].append("Error")
        author_dic["work_id"].append("Error")
        author_dic["two_year_mc"].append("Error")
        author_dic["journal_h_index"].append("Error")
        author_dic["journal_i10"].append("Error")
        author_dic["journal_id"].append("Error")
        print("Error retrieving author information.")

    return author_dic


def make_author_dic():
    """
    Create a dictionary to store author information.

    Returns
    -------
    dict
        A dictionary with keys for author information.
    """
    author_dic = {
        "name": [],
        "orcid": [],
        "dois": [],
        "titles": [],
        "journals": [],
        "years": [],
        "citation_count": [],
        "openalex_id": [],
        "h_index": [],
        "i10": [],
        "work_id": [],
        "two_year_mc": [],
        "journal_h_index": [],
        "journal_i10": [],
        "journal_id": [],
    }
    return author_dic


def scrape(orcids, papers_all, limit=10, fetch_orcids=False):
    """ """
    # check which authors need to be looked up
    to_lookup = orcids[~orcids["orcid"].isin(papers_all.orcid)].reset_index(drop=True)
    print(len(to_lookup))

    author_dic = make_author_dic()

    for i, row in to_lookup.iterrows():
        if i >= limit:
            break
        else:
            pass
        name = row["name_orig"].strip()
        ORCID = row["orcid"].strip()
        print(name, ORCID)
        if fetch_orcids:
            ORCID = ut.get_orcids(name, limit)
            print(ORCID)
        else:
            pass

        if pd.isna(row.openalex_id) or row.openalex_id == "Error":
            openalex_id = None
        else:
            openalex_id = row.openalex_id.strip()

        sleep(5)
        scrape = lookup_open_alex(ORCID, author_dic, name, openalex_id=openalex_id)
        save_json(scrape, f"{output_fol}scrape.json")
    save_papers(author_dic, papers_all, output_fol)
    print("Scraping complete.")
    return author_dic


def name_open_alex(AUTHOR_NAME, AFFILIATION):
    """
    Look up an author on OpenAlex using their name and affiliation.
    Retrieve the author's papers and print their titles and publication years.

    Parameters
    ----------
    AUTHOR_NAME : str or list
        The name of the author to search for.
    AFFILIATION : str
        The affiliation to filter papers by (default is "University of Oxford").

    Returns
    -------
    None
    """
    if isinstance(AUTHOR_NAME, list):
        AUTHOR_NAME = "+".join(AUTHOR_NAME)
    elif isinstance(AUTHOR_NAME, str):
        pass
    else:
        print("Author name must be a string or a list of strings")
        return
    # Search author
    author_url = f"https://api.openalex.org/authors?search={AUTHOR_NAME}+{AFFILIATION}"
    response = requests.get(author_url)
    author_data = response.json()["results"]
    print(response.json()["results"])

    if author_data:
        author_id = author_data[0]["id"]
        papers_url = f"https://api.openalex.org/works?author.id={author_id}"
        papers_response = requests.get(papers_url)
        papers = papers_response.json()["results"]

        for paper in papers[:5]:  # Limit output
            print(
                f"{paper['title']} ({paper['publication_year']}) - "
                f"{paper.get('host_venue', {}).get('name', 'Unknown')}"
            )
    else:
        print("Author not found.")


def process_papers(papers_all, papers_old, correct):
    """
    Process the papers data by renaming columns and merging with the correct data.

    Parameters
    ----------

    papers_all : DataFrame
        The DataFrame containing all papers.
    papers_old : DataFrame
        The DataFrame containing old papers.
    correct : DataFrame
        The DataFrame containing confirmed correct ORCIDs.

    Returns
    -------
    DataFrame
        The processed papers DataFrame.
    """

    # Filter out rows with missing ORCID in papers_all
    papers_new = papers_all[papers_all["orcid"].isin(correct["orcid"])]

    papers_old = papers_old.loc[:, dt.COLS_OLD_PAPER]
    papers_old = papers_old.rename(
        columns={
            "Source title": "Journal",
            "Cited by": "Citation Count",
        }
    )
    papers_new = papers_all.loc[:, dt.COL_RENAME.keys()]
    papers_new = papers_new.rename(columns=dt.COL_RENAME)

    papers = pd.concat([papers_new, papers_old], ignore_index=True)
    papers = papers.drop_duplicates(subset=["DOI"], keep="first")
    correct = correct.loc[:, ["name_orig", "orcid", "i10", "h_index"]]
    correct = correct.rename(columns={"name_orig": "Name"})
    correct.orcid = "https://orcid.org/" + correct.orcid.str.strip()
    papers = pd.merge(papers, correct, on="Name", how="left")

    papers.to_csv(f"{output_fol}papers.csv", index=False)
    print


for i in range(50):
    scrape(correct, papers_all, limit=50, fetch_orcids=False)
