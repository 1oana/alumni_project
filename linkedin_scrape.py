import pandas as pd
from selenium import webdriver
from linkedin_scraper import Person, actions
import credentials as cd  # Ensure this contains your email and password variables

print("Packages imported")

# Setup WebDriver
driver = webdriver.Chrome()
print("Driver acquired")

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
