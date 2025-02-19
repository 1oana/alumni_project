import pandas as pd
# from selenium import webdriver
# from linkedin_scraper import Person, actions
import credentials as cd  # Ensure this contains your email and password variables
import requests
import json
from time import sleep
import os

output = "output/"

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
linkedin_profiles = [
    "https://www.linkedin.com/in/ioana-duta/"
]


# Function to fetch employment history
def get_employment_history(linkedin_url):
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


li_loc = f"{output}linkedin_scrape/"
jsons_loc = f"{li_loc}jsons/"
seen_profiles_fname = f"{li_loc}seen_profiles.txt"

with open(seen_profiles_fname, "r") as file:
    seen_profiles = file.read().split(",")
linkedin_profiles = pd.read_csv(f"{output}csv/no_career.csv")
linkedin_profiles = linkedin_profiles[~linkedin_profiles.Name.isin(seen_profiles)]

limit = 11
names = linkedin_profiles.Name[:limit]
profiles = linkedin_profiles.Site[:limit]
# read list of seen profiles

i = 0
available_jsons = os.listdir(jsons_loc)
for json_file in available_jsons:
    with open(f"{jsons_loc}{json_file}", "r") as file:
        data = json.load(file)

    if data == {}:
        i+=1
        print(json_file)
        # save elsewhere
        os.rename(f"{jsons_loc}{json_file}", f"{li_loc}failed/{json_file}")
        print(f"Failed {json_file}")
    else:
        pass
print(i)

collect = False
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
                data = get_employment_history(profile)
                
                # save data to new json file
                with open(f"{jsons_loc}{json_name}.json", "w") as file:
                    json.dump(data, file)

                with open(seen_profiles_fname, "a") as file:
                    seen_to_write = ','.join(seen_profiles)
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
