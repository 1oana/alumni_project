import requests
import json
from credentials import SCOPUS_API_KEY, SS_KEY
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from time import sleep

limit = 1000


def save_text_file(filename, data):
    with open(filename, "w") as f:
        f.write(data)


def load_json(filename):
    with open(filename) as f:
        return json.load(f)


def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)


#########
# API
#########

def scrape(orcids, papers_all, output_fol, limit=limit):
    # check which authors need to be looked up
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


def get_papers_elsevier(author_name, affiliation, limit=limit):
    headers = {"X-ELS-APIKey": SCOPUS_API_KEY, "Accept": "application/json"}

    text = f"Searching for papers by {author_name} from {affiliation}..."

    # Step 1: Search for Author by Name and Affiliation
    els_url = "https://api.elsevier.com/content/search/author"
    author_url = f"{els_url}?query=authlast"
    full_author_search_url = (
        f"{author_url}({author_name.split()[-1]})%20and%20affil({affiliation})"
    )
    response = requests.get(full_author_search_url, headers=headers)

    if response.status_code == 200:
        author_data = response.json()
        if "search-results" in author_data and "entry" in author_data["search-results"]:
            authors = author_data["search-results"]["entry"]
            if authors:
                author_id = authors[0]["dc:identifier"].split(":")[
                    -1
                ]  # Extract Scopus Author ID

                text += f"\nFound Author: {authors[0]['preferred-name']['surname']}, "
                text += f"{authors[0]['preferred-name']['given-name']}"
                text += f"\nScopus Author ID: {author_id}"

                # Step 2: Get Author's Papers
                papers_url = f"{els_url}content/search/scopus?query=AU-ID({author_id})"
                papers_response = requests.get(papers_url, headers=headers)

                if papers_response.status_code == 200:
                    papers_data = papers_response.json()
                    papers = papers_data.get("search-results", {}).get("entry", [])

                    text += "\\nnRecent Papers:"
                    for paper in papers[:limit]:  # Limit to 5 papers
                        title = paper.get("dc:title", "Unknown Title")
                        year = paper.get("prism:coverDate", "Unknown Year").split("-")[
                            0
                        ]
                        journal = paper.get("prism:publicationName", "Unknown Journal")
                        doi = paper.get("prism:doi", "No DOI Available")
                        text += f"\n- {title} ({year}) - {journal} [DOI: {doi}]"
                else:
                    text += "\nFailed to retrieve papers."
            else:
                text += "\nAuthor not found."
        else:
            text += "\nNo author data available."
    else:
        print(f"Error {response.status_code}: {response.text}")

    return text


# Function to fetch an author's Semantic Scholar ID using ORCID
def get_semantic_author_id(orcid, api_key):
    ss_url = "https://api.semanticscholar.org/"
    query = f"{orcid}&fields=authorId,name"
    query = f"{'https://orcid.org/' + orcid}"
    url = f"{ss_url}graph/v1/author/search?query={query}"
    headers = {"x-api-key": api_key}

    response = requests.get(url, headers=headers)
    print(response.json())
    print('=========')
    print(response.status_code)

    if response.status_code == 200:
        authors = response.json().get("data", [])
        if authors:
            return authors[0]["authorId"], authors[0]["name"]
    return None, None


def get_papers_semantic(name, orcid):
    # Search for author
    ss_url = "https://api.semanticscholar.org/"
    headers = {"x-api-key": SS_KEY}

    # Find matching author based on affiliation
    author_id, author_name = get_semantic_author_id(orcid, SS_KEY)

    dic = {
        "name_orig": [],
        "name_srcd": [],
        "orcid": [],
        "ss_id": [],
        "dois": [],
        "titles": [],
        "journals": [],
        "years": [],
        "citation_count": [],
    }
    if author_id:
        # Fetch papers by this author
        fields = "papers.title,papers.year,papers.journal,papers.venue"
        papers_url = f"{ss_url}graph/v1/author/{author_id}?fields={fields}"
        response = requests.get(papers_url, headers=headers)
        papers = response.json().get("papers", [])

        for paper in papers:
            print(paper)

            dic["name_orig"].append(name)
            dic["name_srcd"].append(author_name)
            dic["orcid"].append(orcid)
            dic["ss_id"].append(author_id)
            dic["dois"].append("Unknown")
            dic["titles"].append(paper["title"])
            dic["journals"].append(paper.get("journal", paper.get("venue", "Unknown")))
            dic["years"].append(paper["year"])
            dic["citation_count"].append("Unknown")

        return dic
    else:
        print("Author not found.")


def get_papers_cross_ref(author_name, affiliation, limit=limit):
    # query = f"{author_name} {affiliation}"
    if isinstance(author_name, list):
        author_query = (
            f"query.author={author_name[0]} AND query.author={author_name[1]}"
        )
    elif isinstance(author_name, str):
        author_query = f"query.author='{author_name}'"
    else:
        print("Author name must be a string or a list of strings")
        return
    query = f"{author_query} AND query.affiliation={affiliation}"
    # facet = f"facet=affiliation:{affiliation}"
    facet = ""
    mailto = "mailto:ioana.duta@ndcn.ox.ac.uk"
    crossref_url = f"https://api.crossref.org/works?{query}{facet}{mailto}"
    response = requests.get(crossref_url)

    print("json keys", response.json().keys())
    print("message keys", response.json()["message"].keys())
    print("total responses", response.json()["message"]["total-results"])
    print(response.json()["message"]["items"][0].keys())
    print("=========================================")
    papers = response.json()["message"]["items"]
    print("=========================================")
    for paper in papers[:limit]:  # Limit output
        print(paper["title"])
        print(paper["DOI"])
        print(paper["author"])
        print("\n\n\n")
        print("=========================================")


def plotmiss(Xy, n, cmap, label_list, cat_cols=[], filename=None, savefig=False):
    """
    creates an encoded copy of the data such that:
        - Explained missing values are -2
        - Unexplained missing values are -1
        - 'no' values are 0
        - 'yes' values are 1
        - other values are 2
    Which of these labels to use is specified in the inputs.
    Then plots a visualisation of above
    Keyword arguments:
        Xy (dataframe): the data to encode/visualise
        n (int): number of labels
        cmap (list): colours for the plot, each corresponding to a label
        label_list (list): list of labels by which to encode the data
            subset of (-2, -1, 0, 1, 2)
        cat_cols (list): names of columns with categorical variables
        filename: what to save the plot as
    Returns:
        miss (dataframe): encoded data
    """
    miss = Xy.copy()

    # make this a string so theres no pesky find and replace errors
    miss = miss.applymap(str)

    # special cases
    nanlist = ["nan", np.nan, str(np.nan), str(pd.NA), str(pd.NaT)]
    onelist = ["True", "Yes", "1", "1.0"]
    nolist = ["False", "No", "0", "0.0"]

    # iterate through and replace as appropriate:
    # -2 = expected missingness, -1 = unexpected missingness,
    # 0 = no, 1 = yes, 2 = other (eg categorical value given)
    for c in miss.columns:
        col = list(miss[c])

        rep_col = col.copy()
        if c in cat_cols:
            for j, m in enumerate(col):
                if m in nanlist:
                    rep_col[j] = "-1"
                else:
                    rep_col[j] = "2"
        else:
            for j, m in enumerate(col):
                if m in onelist:
                    rep_col[j] = "1"
                elif m in nolist:
                    rep_col[j] = "0"
                elif m in nanlist:
                    rep_col[j] = "-1"
                else:
                    rep_col[j] = "2"
        miss[c] = rep_col

    # and finally back to integers!
    miss = miss.applymap(int)
    # sns.set(rc={'figure.figsize':figsize})

    hm = sns.heatmap(
        miss, annot=False, yticklabels=False, xticklabels=1, cmap=cmap, linewidths=0
    )

    plt.xticks(plt.xticks()[0], rotation=45, horizontalalignment="right", fontsize=10)

    colorbar = hm.collections[0].colorbar
    r = colorbar.vmax - colorbar.vmin
    colorbar.set_ticks(
        [
            colorbar.vmin + r / len(label_list) * (0.5 + i)
            for i in range(len(label_list))
        ]
    )
    colorbar.set_ticklabels(
        label_list, size=10, rotation=270, verticalalignment="center"
    )

    if savefig:
        plt.savefig(filename + ".png")

    plt.show()
    return miss
