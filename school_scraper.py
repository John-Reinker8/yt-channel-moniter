import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import pandas as pd
from fake_useragent import UserAgent


def process_csvs(folder_path):
    count = 0
    school_tuples = []
    seen_tuples = set()
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)

        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, on_bad_lines='skip')
            print(file_path)
            if 'Listing Title' in df.columns and 'Listing State' in df.columns:
                for _, row in df.iterrows():
                    school_name = row['Listing Title']
                    state = row['Listing State']
                    school_tuple = (school_name, state)

                    if school_tuple not in seen_tuples:
                        school_tuples.append(school_tuple)
                        seen_tuples.add(school_tuple)

                count += 1

            else:
                print('Error with finding specified columns')
        
        else:
           print('Error with finding .csv file')

    print (len(school_tuples))
    df_tuples = pd.DataFrame(school_tuples, columns=['School Name', 'State'])
    df_tuples.to_csv('school_tuples.csv', index=False)

    return school_tuples

def load_school_tuples(file_path):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        school_tuples = list(df.itertuples(index=False, name=None))
        return school_tuples
    else:
        print(f"No saved school tuples found at {file_path}")
        return None



def get_school_links(school_tuples):
    ua = UserAgent()
    user_agent = ua.random
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    ## options.add_argument('--headless')
  

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


    school_links = []
    count = 0
    errors = 0

    for tuple in school_tuples:
        school_name, state = tuple

        q = f"{school_name} {state} website"
        url = f"https://www.google.com/search?q={q.replace(' ', '+')}"
        driver.get(url)

        try:
            wait = WebDriverWait(driver, 10)
            results = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="yuRUbf"]//a')))
            result = results[0]
            school_links.append(result.get_attribute('href'))
            count += 1
        
        except Exception as e:
            print(f"Error for {school_name} {state}: {e}")
            errors += 1
            continue

        time.sleep(random.uniform(1, 5))

    driver.quit()
    print(f"Number of links: {count}")
    print(f"Number of errors: {errors}")

    return school_links


def main():
    
    folder_path = '/Users/johnreinker/Desktop/dados2'
    tuples_path = 'school_tuples.csv'

    school_tuples = load_school_tuples(tuples_path)
    if school_tuples is None:
        school_tuples = process_csvs(folder_path)
    
    school_links = get_school_links(school_tuples)

    print (school_links)


if __name__ == "__main__":
    main()