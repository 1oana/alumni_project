import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotnine as p9
from plotnine import ggplot, aes


output = "output/csv/"
input = "input/"
figures = "figures/"
uk = ["England", "Scotland", "Wales", "Northern Ireland"]

papers = pd.read_csv(f"{output}papers.csv")
students = pd.read_excel(f"{input}students.xlsx", sheet_name="Students")

to_exclude = [0, "0", np.nan, "nan", "None", "none", "", "Not Found", "Error"]


######
# PAPERS
######

# histogram of citation count
papers["citation_count"] = papers["citation_count"].astype(float)
citation_counts = papers[papers["citation_count"] < 100]
# .value_counts().reset_index()
citation_histogram = (
    ggplot(citation_counts, aes("citation_count"))
    + p9.geom_histogram(binwidth=1)
    + p9.theme_bw()
    + p9.labels.ggtitle("Histogram of Citation Counts (counts under 100)")
    # + p9.scale_x_log10()
)
citation_histogram.save(f"{figures}citations_hist.png")

# histogram of number of papers per student
papers_per_student = papers["name_srcd"].value_counts().reset_index()
papers_per_student.columns = ["name_srcd", "papers"]
papers_per_student = papers_per_student.sort_values("papers", ascending=False)
papers_per_student["papers"] = papers_per_student["papers"].astype(float)
papers_per_student.plot(kind="hist", bins=20)
plt.savefig(f"{figures}papers_per_student_hist.png")

# bar chart of publication year
papers["years"] = papers["years"].str.replace(".0", "")
papers["years"] = papers["years"].astype(float)
# papers['years'] = papers['years'].astype(int)
papers_per_year = papers[papers["years"] > 2002]["years"].value_counts().reset_index()
papers_per_year.columns = ["years", "papers"]
papers_per_year = papers_per_year.sort_values("years")
plt.bar(papers_per_year["years"], papers_per_year["papers"])
# andgle the x-axis labels
plt.xticks(rotation=45)
plt.savefig(f"{figures}papers_per_year.png")
plt.close()

# remove text in brackets
limit = 10
papers["journals"] = papers["journals"].str.replace(r"\(.*\)", "")
journals = papers["journals"].value_counts().reset_index()
journals.columns = ["journals", "papers"]
journals = journals.sort_values("papers", ascending=False)
other = journals[journals["papers"] < limit]
journals = journals[journals["papers"] > limit]
journals.loc[len(journals)] = ["Other", other["papers"].sum()]
sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 10))
plt.pie(journals["papers"], labels=journals["journals"], autopct="%1.1f%%")
plt.axis("equal")
plt.title("Distribution of Papers by Journal")
plt.savefig(f"{figures}journals_pie.png")
plt.close()

########
# PRE DTC
########
limit = 5
# looking at where syudents went to university before the PhD
for abbr, full in zip(["UG", "PG"], ["Undergraduate", "Postgraduate"]):
    for col in ["Country", "University", "Category"]:
        counts = students[students[f"{abbr}{col}"] != 0]
        counts = counts[f"{abbr}{col}"].value_counts().reset_index()
        counts.columns = [col, "students"]
        other = counts[counts["students"] < limit]
        counts = counts[counts["students"] > limit]
        counts.loc[len(counts)] = ["Other", other["students"].sum()]
        counts = counts.sort_values("students", ascending=False)
        plt.pie(counts["students"], labels=counts[col], autopct="%1.1f%%")
        plt.axis("equal")
        plt.title(f"Distribution of {full} Degree {col}")
        plt.savefig(f"{figures}{abbr}_{col}_pie.png")
        plt.close()

# graduates by sector
counts = students["Sector"].value_counts().reset_index()
counts.columns = ["index", "Sector"]
plt.pie(counts["Sector"], labels=counts["index"], autopct="%1.1f%%")
plt.axis("equal")
plt.title("Distribution of Graduates by Sector")
plt.savefig(f"{figures}sector_pie.png")
plt.close()

# graduates by country
limit = 3
counts = students["Country"].value_counts().reset_index()
counts.columns = ["index", "Country"]
counts = counts.sort_values("Country", ascending=False)
other = counts[counts["Country"] < limit]
counts = counts[counts["Country"] > limit]
counts.loc[len(counts)] = ["Other", other["Country"].sum()]
plt.pie(counts["Country"], labels=counts["index"], autopct="%1.1f%%")
plt.axis("equal")
plt.title("Distribution of Graduates by Country")
plt.savefig(f"{figures}country_pie.png")
plt.close()

# how many in each continent
counts = students["Continent"].value_counts().reset_index()
counts.columns = ["index", "Continent"]
plt.pie(counts["Continent"], labels=counts["index"], autopct="%1.1f%%")
plt.axis("equal")
plt.title("Distribution of Graduates by Continent")
plt.savefig(f"{figures}continent_pie.png")
plt.close()

# distribution by continent
by_continent = False
if by_continent:
    for continent in students["Continent"].unique():
        limit = 1
        counts = students[students["Continent"] == continent]
        counts = counts["Country"].value_counts().reset_index()
        counts.columns = ["index", "Country"]
        counts = counts.sort_values("Country", ascending=False)
        other = counts[counts["Country"] < limit]
        counts = counts[counts["Country"] > limit]
        counts.loc[len(counts)] = ["Other", other["Country"].sum()]
        plt.pie(counts["Country"], labels=counts["index"], autopct="%1.1f%%")
        plt.axis("equal")
        plt.title(f"Distribution of Graduates by Country in {continent}")
        plt.savefig(f"{figures}{continent}_country_pie.png")
        plt.close()

# europe without the UK
limit = 2
counts = (
    students[students["Continent"] == "Europe"]["Country"].value_counts().reset_index()
)
counts.columns = ["index", "Country"]
counts = counts.sort_values("Country", ascending=False)
counts = counts[counts["index"] != "United Kingdom"]
other = counts[counts["Country"] < limit]
counts = counts[counts["Country"] > limit]
counts.loc[len(counts)] = ["Other", other["Country"].sum()]
counts.columns = ["index", "Country"]
plt.pie(counts["Country"], labels=counts["index"], autopct="%1.1f%%")
plt.axis("equal")
plt.title("Distribution of European Graduates by Country (excluding UK)")
plt.savefig(f"{figures}europe_nouk_country_pie.png")
plt.close()

# if UK, where are they?
limit = 4
counts = (
    students[students["Country"] == "United Kingdom"]["City"]
    .value_counts()
    .reset_index()
)
counts.columns = ["index", "City"]
counts = counts.sort_values("City", ascending=False)
other = counts[counts["City"] < limit]
counts = counts[counts["City"] > limit]
counts.loc[len(counts)] = ["Other", other["City"].sum()]
plt.pie(counts["City"], labels=counts["index"], autopct="%1.1f%%")
plt.axis("equal")
plt.title("Distribution of UK Graduates by City")
plt.savefig(f"{figures}uk_city_pie.png")
plt.close()

# stacked bar chart of students by course and year
students["Year"] = students["Year"].astype(int)
students["Course"] = students["Course"].astype(str)
counts = students.groupby(["Year", "Course"]).size().unstack()
counts = counts.fillna(0)
counts.plot(kind="bar", stacked=True)
# make legend smaller
plt.legend(loc="upper left", bbox_to_anchor=(0, 1), ncol=1)
plt.title("Distribution of Students by Course and Year")
plt.savefig(f"{figures}course_year_bar.png")
plt.close()

# whether graduates moved university between UG and PG
for col, place in zip(["Country", "University"], ["England", "Oxford"]):
    counts = students.loc[:, [f"UG{col}", f"PG{col}"]]
    counts["same_place"] = None
    counts.loc[counts[f"UG{col}"] == counts[f"PG{col}"], "same_place"] = (
        f"Stayed (not at {place})"
    )
    counts.loc[counts[f"UG{col}"] != counts[f"PG{col}"], "same_place"] = (
        f"Moved\n(not involving {place})"
    )
    counts.loc[
        (counts[f"UG{col}"].isna()) & (counts[f"PG{col}"].isna()), "same_place"
    ] = "Not Known"
    # if both UG and PG were Oxford, mark as such
    counts.loc[
        (counts[f"UG{col}"] == place) & (counts[f"PG{col}"] == place),
        "same_place",
    ] = f"Stayed in {place}"
    counts.loc[
        (counts[f"UG{col}"] != place) & (counts[f"PG{col}"] == place),
        "same_place",
    ] = f"Moved to {place}"
    counts.loc[
        (counts[f"UG{col}"] == place) & (counts[f"PG{col}"] != place),
        "same_place",
    ] = f"Moved from {place}"
    counts = counts["same_place"].value_counts().reset_index()
    counts.columns = ["index", "same_place"]
    plt.pie(counts["same_place"], labels=counts["index"], autopct="%1.1f%%")
    plt.axis("equal")
    plt.title(f"Did Students Change {col} Between UG and PG Study?")
    plt.savefig(f"{figures}study_{col.lower()}_change_pie.png")
    plt.close()

# Between UG/PG study and graduating from DTC, did graduates stay in Oxford?
counts = students.loc[:, ["PGUniversity", "City"]]
counts["last_known"] = counts["PGUniversity"].copy()
counts.loc[counts["last_known"].isna(), "last_known"] = students["UGUniversity"]
counts["place"] = None
counts.loc[counts["last_known"] == counts["City"], "place"] = "Stayed (Other)"
counts.loc[counts["last_known"] != counts["City"], "place"] = "Moved (Other)"
counts.loc[
    (counts["last_known"].isna()) & (counts["City"].isna()), "place"
] = "Not Known"
counts.loc[
    (counts["last_known"] == 'Oxford') & (counts["City"] == 'Oxford'), "place"
] = "Stayed in Oxford"
counts.loc[
    (counts["last_known"] != 'Oxford') & (counts["City"] == 'Oxford'), "place"
] = "Moved to Oxford"
counts.loc[
    (counts["last_known"] == 'Oxford') & (counts["City"] != 'Oxford'), "place"
] = "Moved Away From Oxford"
counts = counts["place"].value_counts().reset_index()
counts.columns = ["index", "place"]
plt.pie(counts["place"], labels=counts["index"], autopct="%1.1f%%")
plt.axis("equal")
plt.title("Between UG/PG study and graduating from DTC, did graduates stay in Oxford?")
plt.savefig(f"{figures}oxford_change_pie.png")
plt.close()

# whether graduates moved university between UG and PG
counts = students.loc[:, ["PGCountry", "Country"]]
counts["last_known"] = counts["PGCountry"].copy()
counts.loc[counts["last_known"].isna(), "last_known"] = students["UGCountry"]
counts["same_place"] = None
counts.loc[counts["last_known"] == counts["Country"], "same_place"] = (
    "Stayed (not in UK)"
)
counts.loc[counts["last_known"] != counts["Country"], "same_place"] = (
    "Moved\n(not involving UK)"
)
counts.loc[
    (counts["last_known"].isna()) & (counts["Country"].isna()), "same_place"
] = "Not Known"
# if both UG and PG were Oxford, mark as such
counts.loc[
    (counts["last_known"].isin(uk)) & (counts["Country"] == "United Kingdom"),
    "same_place",
] = "Stayed in UK"
counts.loc[
    (~counts["last_known"].isin(uk)) & (counts["Country"] == "United Kingdom"),
    "same_place",
] = "Moved to UK"
counts.loc[
    (counts["last_known"].isin(uk)) & (counts["Country"] != "United Kingdom"),
    "same_place",
] = "Moved from UK"
counts = counts["same_place"].value_counts().reset_index()
counts.columns = ["index", "same_place"]
plt.pie(counts["same_place"], labels=counts["index"], autopct="%1.1f%%")
plt.axis("equal")
plt.title("Between UG/PG study and graduating from DTC, did graduates move country?")
plt.savefig(f"{figures}country_change_pie.png")
plt.close()

##########
# PROGRESS
##########
# how many entries per year are filled?
cbar = sns.color_palette("prism", 3)
missingness = students.notna().astype(str)
missingness[missingness == "True"] = "1"
missingness[missingness == "False"] = "0"
missingness[students == 0] = "-1"
missingness = missingness.astype(int)
missingness = missingness.loc[:, ["Career History", "Job Title", "UGDegree"]]
label_list = ["Not Found", "Not Filled", "Filled"]
hm = sns.heatmap(
    missingness, annot=False, yticklabels=False, xticklabels=1, cmap=cbar, linewidths=0
)
plt.xticks(plt.xticks()[0], rotation=0, horizontalalignment="right", fontsize=10)
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
plt.title("Missingness of Entries in the Student Data")
plt.savefig(f"{figures}missingness_plot.png")
plt.close()
