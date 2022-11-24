from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from utils import send_an_email
import pandas as pd
import schedule
import time

def job():

    chromeOptions = Options()
    chromeOptions.add_argument("--headless")
    driver = webdriver.Chrome(options=chromeOptions)

    # Wait for page to load before scraping
    driver.implicitly_wait(5) 
    apartments = []

    url = "https://sssb.se/en/looking-for-housing/apply-for-apartment/available-apartments/available-apartments-list/?paginationantal=100"
    driver.get(url)

    res = driver.find_element(By.XPATH, "//*[@id='SubNavigationContentContainer']/div[3]/div[4]/div")

    df = pd.DataFrame(columns = ["Area", "Address", "Type", "Floor", "Living space", "Rent", "Moving date", "Days"])

    apartments = res.text.split("\n")
    rows = [apartments[i:i + 8] for i in range(0, len(apartments), 8)]

    driver.close()

    df = df.append(pd.DataFrame(rows, columns=df.columns))
    df[["Days", "Students"]] = df["Days"].apply(lambda x: pd.Series(str(x).split(" (")))
    df["Students"] = df["Students"].apply(lambda x: pd.Series(x[:1]))

    ideal_apartments = df[(df["Area"] == "Birka") | (df["Type"].str.startswith("2 rooms"))].sort_values(["Area", "Days"])

    # The below code checks if the apartments were changed from the latest scrape. This is done by grabbing the previous scrapped "ideal apartments" and checking their address (i.e. building name & room number) with the newly scrapped ones.
    # If there was a change, the ideal ones are saved and sent to email.
    # Otherwise, nothing is done!

    previous_ideal = pd.read_csv("previous_ideal.csv")
    ideal_apartments = ideal_apartments.reset_index()

    compare = ideal_apartments["Address"].compare(previous_ideal["Address"])

    if len(compare) != 0:
        print("There was an update in the listings!")
        ideal_apartments.to_csv("previous_ideal.csv",index=False)
        send_an_email(ideal_apartments)

schedule.every(1).minutes.do(job)
#schedule.every().day.at('10:00').do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
