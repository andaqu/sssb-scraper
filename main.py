from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from utils import send_an_email
import pandas as pd

chromeOptions = Options()
chromeOptions.add_argument("--headless")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chromeOptions)

# Wait for page to load before scraping
driver.implicitly_wait(5) 
apartments = []

url = "https://sssb.se/en/looking-for-housing/apply-for-apartment/available-apartments/available-apartments-list/?paginationantal=100"
driver.get(url)

# Scrape apartment information (res) and links (res_links)
res = driver.find_element(By.XPATH, "//*[@id='SubNavigationContentContainer']/div[3]/div[4]/div")
res_links = driver.find_elements(By.XPATH, "//*[@id='SubNavigationContentContainer']/div[3]/div[4]/div/a")

# Build dataframe, populate the scraped data, and pre-process it
df = pd.DataFrame(columns = ["Area", "Address", "Type", "Floor", "Living space", "Rent", "Moving date", "Days"])

apartments = res.text.split("\n")
rows = [apartments[i:i + 8] for i in range(0, len(apartments), 8)]
df = df.append(pd.DataFrame(rows, columns=df.columns))

df[["Days", "Students"]] = df["Days"].apply(lambda x: pd.Series(str(x).split(" (")))
df["Students"] = df["Students"].apply(lambda x: pd.Series(x[:1]))
df["Link"] = [e.get_attribute('href') for e in res_links]

# Once the driver is closed, res and res_links cannot be accessed!
driver.close()

# ~df["Area"].isin(["Flemingsberg", "Strix"])
conditions_for_ideal =  (df["Area"] == "Birka") | (df["Type"] == "2 rooms & kitchen") | (df["Living space"].astype(int) >= 28)
ideal_apartments = df[conditions_for_ideal].sort_values(["Area", "Days"])

# The below code checks if the apartments were changed from the latest scrape. This is done by grabbing the previous scrapped "ideal apartments" and checking their address (i.e. building name & room number) with the newly scrapped ones.
# If there was a change, the ideal ones are saved and sent to email.
# Otherwise, nothing is done!

previous_ideal = pd.read_csv("previous_ideal.csv")
ideal_apartments = ideal_apartments.reset_index(drop=True)

# From the previously identified ideal apartments, which are the new apartments?
changes = ideal_apartments["Address"][~ideal_apartments["Address"].isin(previous_ideal["Address"])].drop_duplicates()

if not changes.empty:
    print("There was an update in the listings!")

    # Populate the changes table with the needed information to comprehensively send it via email
    changes = pd.merge(changes, ideal_apartments[["Address", "Type", "Area", "Link"]], on=["Address"])

    # The link is only needed for email output, drop it before saving
    # ideal_apartments.drop(["Link"], axis=1).to_csv("previous_ideal.csv",index=False)

    send_an_email(ideal_apartments, changes)
else:
    print("No update in listings!")