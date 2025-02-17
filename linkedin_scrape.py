import pandas as pd
from selenium import webdriver
from linkedin_scraper import Person, actions
import credentials as cd  # Ensure this contains your email and password variables
import requests

print("Packages imported")

# # Setup WebDriver
# driver = webdriver.Chrome()
# print("Driver acquired")

API_KEY = "your_pdl_api_key"
person_url = "https://api.peopledatalabs.com/v5/person/enrich"

params = {
    "api_key": API_KEY,
    "profile": "linkedin.com/in/example-profile"
}

response = requests.get(person_url, params=params)








import requests
import pandas as pd

# Your PDL API Key
API_KEY = "your_pdl_api_key"

# List of LinkedIn Profile URLs to look up
linkedin_profiles = [
    "https://www.linkedin.com/in/example1",
    "https://www.linkedin.com/in/example2",
    "https://www.linkedin.com/in/example3"
]


# Function to fetch employment history
def get_employment_history(linkedin_url):
    url = "https://api.peopledatalabs.com/v5/person/enrich"
    params = {"api_key": API_KEY, "profile": linkedin_url}

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        full_name = data.get("full_name", "Unknown")
        experiences = data.get("experience", [])

        employment_history = []
        for job in experiences:
            employment_history.append({
                "LinkedIn": linkedin_url,
                "Full Name": full_name,
                "Job Title": job.get("title", "Unknown"),
                "Company": job.get("company", "Unknown"),
                "Start Date": job.get("start_date", "Unknown"),
                "End Date": job.get("end_date", "Present")
            })
        
        return employment_history
    else:
        print(f"Error for {linkedin_url}: {response.status_code}")
        return []


# Collect data for all profiles
all_employment_data = []
for profile in linkedin_profiles:
    all_employment_data.extend(get_employment_history(profile))

# Convert to DataFrame and save as CSV
df = pd.DataFrame(all_employment_data)
df.to_csv("employment_history.csv", index=False)

print("✅ Employment history saved to 'employment_history.csv'")

if response.status_code == 200:
    person_data = response.json()
    print("Name:", person_data.get("full_name"))
    print("\nEmployment History:")
    for job in person_data.get("experience", []):
        print(f"- {job.get('title')} at {job.get('company')}, {job.get('start_date')} - {job.get('end_date', 'Present')}")
else:
    print("Error:", response.status_code)


try:
    # Login to LinkedIn
    actions.login(driver, cd.email, cd.password)
    print("Logged in")

    input("Press Enter to proceed after completing CAPTCHA if required...")

    # Fetch profile
    person_url = "https://www.linkedin.com/in/ioana-duta"
    person = Person(person_url, driver=driver, scrape=False, close_on_complete=False)
    # Set scrape=True to fetch details
    print("Person acquired:", person)

except Exception as e:
    print("Error:", e)
finally:
    driver.quit()  # Ensure the driver closes


def load_data(filename):
    return pd.read_csv('filename')
