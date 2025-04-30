import pandas as pd

# from selenium import webdriver
# from linkedin_scraper import Person, actions
import credentials as cd  # Ensure this contains your email and password variables
import requests
import json
from time import sleep
import os

output = "output/"
input_fol = "input/"

# Setup WebDriver
# driver = webdriver.Chrome()

API_KEY = "yours_pdl_api_key"
# person_url = "https://api.peopledatalabs.com/v5/person/enrich"

# params = {
#     "api_key": API_KEY,
#     "profile": "linkedin.com/in/example-profile"
# }

# response = requests.get(person_url, params=params)

# Your PDL API Key
API_KEY = cd.PDL_KEY

# List of LinkedIn Profile URLs to look up
linkedin_profiles = ["https://www.linkedin.com/in/ioana-duta/"]
student_data = pd.read_excel(f"{input_fol}students.xlsx", sheet_name="Students")


# Function to fetch employment history
def get_linkedin(linkedin_url):
    url = "https://api.peopledatalabs.com/v5/person/enrich"
    params = {"api_key": API_KEY, "profile": linkedin_url}

    response = requests.get(url, params=params)
    print(response.status_code)

    if response.status_code == 200:
        print(f"Success for {linkedin_url}")
        data = response.json()
        # need data['data']
        return data
    else:
        print(f"Error for {linkedin_url}: {response.status_code}")
        return {}


def get_all_linkedin(linkedin_profiles, seen_profiles, limit=10):
    names = linkedin_profiles.Name[:limit]
    profiles = linkedin_profiles.Site[:limit]

    i = 0
    available_jsons = os.listdir(jsons_loc)
    for json_file in available_jsons:
        with open(f"{jsons_loc}{json_file}", "r") as file:
            data = json.load(file)

        if data == {}:
            i += 1
            print(json_file)
            # save elsewhere
            os.rename(f"{jsons_loc}{json_file}", f"{li_loc}failed/{json_file}")
            print(f"Failed {json_file}")
        else:
            pass
    print(i)

    collect = True
    if collect:
        # Collect data for all profiles
        all_employment_data = []
        i = 0
        for name, profile in zip(names, profiles):
            print(i)
            if i >= limit:
                break
            else:
                pass

            i += 1
            if profile in seen_profiles:
                print(f"Skipping {name}...")
            else:
                seen_profiles.append(name)
                print(f"Fetching data for {name}...")
                available_jsons = os.listdir(jsons_loc)
                data = {}
                json_name = name.lower().replace(" ", "_")
                if f"{json_name}.json" in available_jsons:
                    pass
                else:
                    data = get_linkedin(profile)
                    print(name)

                    # save data to new json file
                    with open(f"{jsons_loc}{json_name}.json", "w") as file:
                        json.dump(data, file)

                    with open(seen_profiles_fname, "a") as file:
                        file.write(f"{name},")

            sleep(10)
            # read and update the list of profiles scanned

        # save as text file
        with open("employment_history.txt", "w") as file:
            file.write(str(all_employment_data))

        # Convert to DataFrame and save as CSV
        df = pd.DataFrame(all_employment_data)
        df.to_csv("employment_history.csv", index=False)

        print("✅ Employment history saved to 'employment_history.csv'")
    return None


li_loc = f"{output}linkedin_scrape/"
jsons_loc = f"{li_loc}jsons/"
seen_profiles_fname = f"{li_loc}seen_profiles.txt"

with open(seen_profiles_fname, "r") as file:
    seen_profiles = file.read().split(",")
linkedin_profiles = pd.read_csv(f"{output}csv/no_career.csv")
linkedin_profiles = linkedin_profiles[~linkedin_profiles.Name.isin(seen_profiles)]
print(f"A total of {linkedin_profiles.shape[0]} remain")

get_linkedin_bool = False
if get_linkedin_bool:
    get_all_linkedin(linkedin_profiles, seen_profiles, limit=10)
jsons = os.listdir(jsons_loc)
columns = [
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


def get_locations(experience):
    company = experience["company"]
    if company is None:
        location = None
    else:
        location = company["location"]

    loc_names = experience["location_names"]
    # option 1: they associated a locality with the job directly
    if location is not None:
        print("Location not none")
        loc_as_str = location["name"]
        city = location["locality"]
        country = location["country"]
        continent = location["continent"]
        if city is None:
            city = location["region"]
            if city is None and isinstance(loc_as_str, str):
                city = loc_as_str.split(", ")[0]
            else:
                city = ""
        else:
            pass

        if country is None and isinstance(loc_as_str, str):
            country = loc_as_str.split(", ")[-1]
        else:
            country = ""

        if continent is None:
            continent = ""
        else:
            pass

    elif loc_names != []:
        print("had to go to loc names")
        loc_names = loc_names[0].split(", ")
        city = loc_names[0]
        country = loc_names[-1]
        continent = ""
    else:
        print("blanks")
        city, country, continent = "", "", ""

    return city, country, continent


history_df = pd.DataFrame(columns=["ID", "Name", "History"])
jobs_df = pd.DataFrame(columns=columns)

process_jsons = True
if process_jsons:
    sectors = []

    for json_file in jsons:
        with open(f"{jsons_loc}{json_file}", "r") as file:
            data = json.load(file)
        data = data.get("data", {})
        if data == {}:
            print(f"Failed {json_file}")
        else:
            pass

        experiences = data.get("experience", [])
        # initialise dictionary
        jobs_dic = {col: [] for col in columns}
        person_name = json_file.replace(".json", "").replace("_", " ").title()
        print(person_name)
        person_id = student_data.loc[student_data.Name.str.title() == person_name, "ID"].values
        year = student_data.loc[student_data.Name.str.title() == person_name, "Year"].values[0]
        li_link = student_data.loc[student_data.Name.str.title() == person_name, "Site"].values[0]
        first_name = data["first_name"]
        last_name = data["last_name"]
        print(person_id)
        try:
            person_id = person_id[0]
        except IndexError as e:
            print(e)
            person_id = "ERROR"

        history = []
        for experience in experiences:
            company = experience.get("company", {})
            if company is None:
                company = {}

            city, country, continent = get_locations(experience)

            jobs_dic["ID"].append(person_id)
            jobs_dic["Name"].append(person_name)
            jobs_dic["Forename"].append(first_name)
            jobs_dic["Surname"].append(last_name)
            jobs_dic["Year"].append(year)
            jobs_dic["Job Title"].append(experience.get("title")["name"])
            jobs_dic["Company"].append(company.get("name"))
            jobs_dic["Start date"].append(experience.get("start_date"))
            jobs_dic["End date"].append(experience.get("end_date", ))
            jobs_dic["Sector"].append(company.get("industry"))
            jobs_dic["Continent"].append(continent)
            jobs_dic["Country"].append(country)
            jobs_dic["City"].append(city)
            jobs_dic["Site"].append(li_link)

            history_to_add = (
                f"{experience.get('title')['name']}, {company.get('name')}, "
            )
            history_to_add += f"{experience.get('start_date')} - {experience.get('end_date', '')}"
            history += [history_to_add]

            sectors = list(set(sectors + [company.get("industry")]))

        jobs_df = pd.concat([jobs_df, pd.DataFrame(jobs_dic)], ignore_index=True)

        # add row in history for this person
        history_df = pd.concat(
            [
                history_df,
                pd.DataFrame.from_dict(
                    {
                        "ID": [person_id],
                        "Name": [person_name],
                        "History": [" / ".join(history)],
                    }
                ),
            ],
            ignore_index=True,
        )

        # history_add = pd.DataFrame.from_dict({'Name': person_name, 'History': "; ".join(history)})
        # pd.concat([history_df, history_add], ignore_index=True)

    jobs_df.to_csv(f"{output}csv/jobs_scrape.csv", index=False)
    history_df.to_csv(f"{output}csv/history.csv", index=False)

    # save sectors
    with open(f"{output}sectors.txt", "w") as file:
        file.write(str(sectors))

# if response.status_code == 200:
#     person_data = response.json()
#     print("Name:", person_data.get("full_name"))
#     print("\nEmployment History:")
#     for job in person_data.get("experience", []):
#         print(f"- {job.get('title')} at {job.get('company')},
#         {job.get('start_date')} - {job.get('end_date', 'Present')}")
# else:
#     print("Error:", response.status_code)

full_scrape = False
if full_scrape:
    try:
        pass
        # Login to LinkedIn
        # actions.login(driver, cd.email, cd.password)
        # print("Logged in")

        # input("Press Enter to proceed after completing CAPTCHA if required...")

        # # Fetch profile
        # person_url = "https://www.linkedin.com/in/ioana-duta"
        # person = Person(person_url, driver=driver, scrape=False, close_on_complete=False)
        # # Set scrape=True to fetch details
        # print("Person acquired:", person)

    except Exception as e:
        print("Error:", e)
    finally:
        pass
        # driver.quit()  # Ensure the driver closes
