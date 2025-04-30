import pandas as pd
import utils as ut
import numpy as np

inputs = "input/"
outputs = "output/"
jsons = f"{outputs}jsons/"
texts = f"{outputs}texts/"

load = True
if load:
    students = pd.read_excel(f"{inputs}students.xlsx", sheet_name="Students")

save_degrees = False
if save_degrees:
    for prefix in ["UG", "PG"]:
        degrees = list(students[f"{prefix}Degree"])

        degrees = list(set(degrees))

        degrees = sorted([str(i) for i in degrees])

        degrees = "\n".join(degrees)

        ut.save_text_file(f"{prefix}degrees.txt", degrees)

save_unis = False
if save_unis:
    for prefix in ["UG", "PG"]:
        universities = list(students[f"{prefix}University"])

        universities = list(set(universities))

        universities = sorted([str(i) for i in universities])

        universities = "\n".join(universities)

        ut.save_text_file(f"{prefix}universities.txt", universities)

    # load replacement jsons as dictionary
    ugr = ut.load_json(f"{jsons}UGuniversities_replace.json")
    pgr = ut.load_json(f"{jsons}PGuniversities_replace.json")

    changed_pg = list({pgr[i] for i in pgr.keys() if i != []})
    unchanged_pg = list({i for i in pgr.keys() if i == []})

    changed_ug = list({ugr[i] for i in ugr.keys() if i != []})
    unchanged_ug = list({i for i in ugr.keys() if i == []})

    all_names = changed_pg + unchanged_pg + changed_ug + unchanged_ug
    all_names = sorted(set(all_names))

    ut.save_text_file(f"{texts}all_universities.txt", "\n".join(all_names))

replace = False
if replace:
    repl = ut.load_json(f"{jsons}universities_replace.json")
    repl = {str(k): v for k, v in repl.items() if v != ""}
    students["PGUniversity_new"] = students["PGUniversity"].replace(repl)
    students["UGUniversity_new"] = students["UGUniversity"].replace(repl)

    students.to_excel("students_replace.xlsx", sheet_name="Students", index=False)

assign_countries = False
if assign_countries:
    # load replacement jsons as dictionary
    countries = ut.load_json(f"{jsons}uni_locations.json")
    students["UGCountry"] = students["UGUniversity"].replace(countries)
    students["PGCountry"] = students["PGUniversity"].replace(countries)
    students.to_excel("students_replace.xlsx", sheet_name="Students", index=False)

assign_categories = False
if assign_categories:
    # load replacement jsons as dictionary
    degrees = ut.load_json(f"{jsons}degrees.json")
    students["UGCategory"] = students["UGDegree"].replace(degrees)
    students["PGCategory"] = students["PGDegree"].replace(degrees)
    students.to_excel("students_replace.xlsx", sheet_name="Students", index=False)

get_degrees = False
if get_degrees:
    pgs = [str(i) for i in students["PGDegree"]]
    ugs = [str(i) for i in students["UGDegree"]]
    pgs = sorted(list(set(pgs)))
    ugs = sorted(list(set(ugs)))

    ut.save_text_file(f"{texts}PGDegrees.txt", "\n".join(pgs))
    ut.save_text_file(f"{texts}UGdegrees.txt", "\n".join(ugs))

uni_jsons = False
if uni_jsons:
    ugr = ut.load_json(f"{jsons}UGuniversities_replace.json")
    pgr = ut.load_json(f"{jsons}PGuniversities_replace.json")
    unis = set(students["UGUniversity"]) | set(students["PGUniversity"])

    repl = {}
    for i in ugr.keys():
        if i not in repl.keys():
            repl[i] = ugr[i]

    for i in pgr.keys():
        if i not in repl.keys():
            repl[i] = pgr[i]

job_columns = [
    "ID",
    "Name",
    "Forename",
    "Surname",
    "Year",
    "Job Title",
    "Company",
    "Start date",
    "End date",
    "Sector",
    "Continent",
    "Country",
    "City",
    "Site",
]

jobs = False
if jobs:
    jobs_from_scrape = pd.read_csv("output/csv/jobs_scrape.csv")
    names_we_have = set(jobs_from_scrape["Name"])
    jobs_dic = {col: [] for col in job_columns}
    names_to_check = []
    jobs_all = "Career History"
    jobs_current = "Job Title"

    for i, row in students.iterrows():
        name = row["Name"]

        if name in names_we_have:
            continue
        else:
            pass
        all_jobs = row[jobs_all]
        current_job = row[jobs_current]
        forename = row["Forename"]
        surname = row["Surname"]
        site = row["Site"]
        year = row["Year"]

        if current_job in [0, "0", np.nan, "Not Known"]:
            pass
        else:
            current_job = current_job.split(" / ")
            current_job = [i.split(", ") for i in current_job]

            for j, job in enumerate(current_job):
                if len(job) != 3:
                    names_to_check += [f"{row.Name}: Current {j}\n"]
                else:
                    dates = job[2].split("-")
                    dates = [i.strip() for i in dates]
                    if len(dates) == 1:
                        dates.append("Present")

                    jobs_dic["ID"].append(row["ID"])
                    jobs_dic["Name"].append(name)
                    jobs_dic["Forename"].append(forename)
                    jobs_dic["Surname"].append(surname)
                    jobs_dic["Year"].append(year)
                    jobs_dic["Job Title"].append(job[0])
                    jobs_dic["Company"].append(job[1])
                    jobs_dic["Start date"].append(dates[0])
                    jobs_dic["End date"].append(dates[1])
                    jobs_dic["Sector"].append(row["Sector"])
                    jobs_dic["Continent"].append(row["Continent"])
                    jobs_dic["Country"].append(row["Country"])
                    jobs_dic["City"].append(row["City"])
                    jobs_dic["Site"].append(site)

        if all_jobs in [0, "0", np.nan, "Not Known"]:
            pass
        else:
            all_jobs = all_jobs.split(" / ")
            all_jobs = [i.split(", ") for i in all_jobs]
            for k, job in enumerate(all_jobs):
                if len(job) != 3:
                    names_to_check += [f"{row.Name}: Past {k}\n"]
                else:
                    dates = job[2].split("-")
                    dates = [i.strip() for i in dates]
                    if len(dates) == 1:
                        dates.append("NA")

                    jobs_dic["ID"].append(row["ID"])
                    jobs_dic["Name"].append(name)
                    jobs_dic["Forename"].append(forename)
                    jobs_dic["Surname"].append(surname)
                    jobs_dic["Year"].append(year)
                    jobs_dic["Job Title"].append(job[0])
                    jobs_dic["Company"].append(job[1])
                    jobs_dic["Start date"].append(dates[0])
                    jobs_dic["End date"].append(dates[1])
                    jobs_dic["Sector"].append("")
                    jobs_dic["Continent"].append("")
                    jobs_dic["Country"].append("")
                    jobs_dic["City"].append("")
                    jobs_dic["Site"].append(site)

    jobs_df = pd.DataFrame(jobs_dic)
    for column in jobs_df.columns:
        try:
            jobs_df[column] = jobs_df[column].str.strip()
        except AttributeError:
            pass
    jobs_df.to_csv("output/csv/jobs_fromold.csv", index=False)

    jobs_all = pd.concat([jobs_df, jobs_from_scrape], ignore_index=True)
    jobs_all.to_csv("output/csv/jobs_all.csv", index=False)
    # names_to_check = list(set(names_to_check))
    names_to_check = "".join(names_to_check)
    # save names_to_check to text file
    with open("output/names_to_check.txt", "w") as f:
        f.write(names_to_check)

match_theses = False
if match_theses:
    theses = pd.read_csv("input/theses.csv")
    theses = theses[theses.Year < 2020]

    student_table = students[students.Year < 2020]
    student_table = student_table[["ID", "Name", "Year", "Course"]]

    # sort supervisor name by first initial
    supervisors = []
    names_not_in_students = [
        f"{row.Student}, {row.Programme}, {row.Year}"
        for _, row in theses.iterrows()
        if row["Student"] not in student_table.Name.to_list()
    ]
    names_not_in_theses = [
        f"{row.Name}, {row.Course}, {row.Year}"
        for _, row in student_table.iterrows()
        if row["Name"] not in theses.Student.to_list()
    ]

    for i, row in theses.iterrows():
        names = row["Supervisor"].split(" / ")
        for j, name in enumerate(names):
            firstname = name.split(" ")[0]
            lastnames = " ".join(name.split(" ")[1:])
            names[j] = f"{lastnames}, {firstname}"
        supervisors += names
    supervisors = sorted(set(supervisors))
    print(len(supervisors))

    with open("output/supervisors.txt", "w") as f:
        f.write("\n".join(supervisors))

    print("in theses not in students", len(names_not_in_students))
    with open("output/names_not_in_students.txt", "w") as f:
        f.write("\n".join(names_not_in_students))

    print("in students not in theses", len(names_not_in_theses))
    with open("output/names_not_in_theses.txt", "w") as f:
        f.write("\n".join(names_not_in_theses))

    theses = theses[
        ["Year", "Programme", "Student", "Supervisor", "Dept", "DPhil Title"]
    ]
    students_with_job = pd.merge(
        student_table,
        theses,
        left_on="Name",
        right_on="Student",
        how="left",
        suffixes=("", "_thesis"),
    )

    students_with_job = students_with_job[
        [
            "ID",
            "Name",
            "Student",
            "Year",
            "Year_thesis",
            "Course",
            "Programme",
            "Supervisor",
            "Dept",
            "DPhil Title",
        ]
    ]

    students_with_job.to_csv("output/csv/students_with_job.csv", index=False)

    print(students_with_job.shape, student_table.shape)

clean_jobs_dates = True
if clean_jobs_dates:
    months = {
        "01": "Jan",
        "02": "Feb",
        "03": "Mar",
        "04": "Apr",
        "05": "May",
        "06": "Jun",
        "07": "Jul",
        "08": "Aug",
        "09": "Sep",
        "10": "Oct",
        "11": "Nov",
        "12": "Dec",
    }
    nans = [0, "0", np.nan, "NA", "Present", "Unknown", "nan"]
    jobs = pd.read_excel("input/students.xlsx", sheet_name="Jobs").astype(str)
    dates = jobs['Start date']
    n_wrong = 0
    for i, row in jobs.iterrows():
        for datetype in ['Start date', 'End date']:
            this_date = row[datetype]
            if this_date in nans:
                new_date = this_date
            elif 'present' in this_date.lower():
                new_date = 'Present'
            else:
                pass
            this_date = this_date.replace(' 00:00:00', '')

            if '2025' in this_date:
                this_date = this_date.replace(' 00:00:00', '')
                old_date = this_date.split('-')
                if len(old_date) == 3:
                    year = '20' + old_date[2]
                    month = old_date[1]
                    day = '01'
                    new_date = '-'.join([year, month, day])
                elif len(old_date) == 2:
                    year = '20' + old_date[1]
                    month = old_date[0]
                    day = '01'
                    new_date = '-'.join([year, month, day])
                elif len(old_date) == 1:
                    if len(old_date[0]) == 4:
                        new_date = old_date[0] + '-01-01'
                        print(new_date)
                    else:
                        new_date = this_date * 1
                else:
                    new_date = this_date * 1
            else:
                old_date = this_date.split('-')
                if len(old_date) == 2:
                    year = old_date[0]
                    month = old_date[1]
                    day = '01'
                    new_date = '-'.join([year, month, day])
                elif len(old_date) == 1:
                    if len(old_date[0]) == 4:
                        new_date = old_date[0] + '-01-01'
                    else:
                        if '#' in old_date[0]:
                            n_wrong += 1
                else:
                    new_date = this_date * 1

            jobs.loc[i, datetype + ' new'] = new_date

    print(jobs.loc[:, ['Start date', 'Start date new', 'End date', 'End date new']].head())
    jobs.to_csv("output/jobs_dates_cleaned.csv", index=False)
    print(n_wrong, i, i*2)
