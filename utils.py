import requests
import json
from credentials import SCOPUS_API_KEY, SEMANTIC_API_KEY
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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


def get_papers_ssemantic():
    AUTHOR_NAME = "John Doe"
    AFFILIATION = "Harvard University"

    # Search for author
    ss_url = "https://api.semanticscholar.org/"
    query = f"{AUTHOR_NAME}&fields=authorId,name,affiliations"
    author_search_url = f"{ss_url}graph/v1/author/search?query={query}"
    headers = {"x-api-key": SEMANTIC_API_KEY}

    response = requests.get(author_search_url, headers=headers)
    authors = response.json().get("data", [])

    # Find matching author based on affiliation
    author_id = None
    for author in authors:
        if AFFILIATION.lower() in str(author.get("affiliations", [])).lower():
            author_id = author["authorId"]
            break

    if author_id:
        # Fetch papers by this author
        fields = "papers.title,papers.year,papers.journal,papers.venue"
        papers_url = f"{ss_url}graph/v1/author/{author_id}?fields={fields}"
        response = requests.get(papers_url, headers=headers)
        papers = response.json().get("papers", [])

        for paper in papers:
            print(
                f"{paper['title']} ({paper['year']}) - ",
                f"{paper.get('journal', paper.get('venue', 'Unknown'))}"
            )
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


def name_open_alex(AUTHOR_NAME, AFFILIATION):
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


def orcid_open_alex(ORCID, author_dic, name_given):
    # Search author
    orcid_text = f"https://orcid.org/{ORCID}"
    author_url = f"https://api.openalex.org/authors/{orcid_text}"
    print(author_url)
    response = requests.get(author_url)
    if response.status_code == 200:
        author_data = response.json()

        if author_data:
            author_id = author_data["id"]
            print(author_id)
            papers_url = f"https://api.openalex.org/works?filter=author.id:{author_id}"
            papers_response = requests.get(papers_url)
            papers = papers_response.json()["results"]

            for paper in papers:
                try:
                    journal = paper["locations"][0]["source"]["display_name"]
                except Exception as e:
                    print(e)
                    journal = "Unknown"

                author_dic["dois"].append(paper["doi"])
                author_dic["name"].append(author_data["display_name"])
                author_dic["orcid"].append(ORCID)
                author_dic["openalex_id"].append(author_id)
                author_dic["titles"].append(paper["title"])
                author_dic["journals"].append(journal)
                author_dic["years"].append(paper["publication_year"])
                author_dic["citation_count"].append(paper["cited_by_count"])

        else:
            print("Author not found.")

        return author_dic
    else:
        print(f"Error {response.status_code}: {response.text}")
        author_dic["dois"].append("Error")
        author_dic["name"].append(name_given)
        author_dic["orcid"].append(ORCID)
        author_dic["openalex_id"].append("Error")
        author_dic["titles"].append("Error")
        author_dic["journals"].append("Error")
        author_dic["citation_count"].append("Error")
        author_dic["years"].append("Error")
        return None


def get_orcids(name, limit):
    url = f"https://pub.orcid.org/v3.0/search/?q={name}&rows={limit}"
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        results = data.get("result", [])

        if results:
            for person in results[:1]:
                orcid_id = person["orcid-identifier"]["path"]
                print(f"ORCID: https://orcid.org/{orcid_id}")
                return orcid_id
        else:
            print("No ORCID ID found for this name.")
            return None
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None


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
