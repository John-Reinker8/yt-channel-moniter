import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.action_chains import ActionChains
import os
import pandas as pd
from fake_useragent import UserAgent
from dotenv import load_dotenv
import threading
import concurrent.futures
from collections import deque

lock = threading.Lock()

## extracts roughly 118k school and state pairs from dados2 file
def process_csvs(folder_path):
    count = 0
    school_tuples = deque()
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

    print(len(school_tuples))
    ## saves the 118k tuples to a csv file so we don't have to rerun this whole function
    df_tuples = pd.DataFrame(school_tuples, columns=['School Name', 'State'])
    df_tuples.to_csv('school_tuples.csv', index=False)

    return school_tuples

## loads the .csv file created by the process_csvs function, if it exists
def load_school_tuples(file_path='school_tuples.csv'): 
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        school_tuples = deque(df.itertuples(index=False, name=None))
        return school_tuples
    else:
        print(f"No saved school tuples found at {file_path}")
        return None

## uses a webdriver and the list of school, state pairs to obtain the school website links
def get_school_links(school_tuples, saved_links, result_queue, position):
    driver = wbdvr_maker(position)


    while school_tuples:
        with lock:
            if not school_tuples:
                break
            school_tuple = school_tuples.popleft()

        school_name, state = school_tuple
        print(f"Thread {threading.current_thread().name} is working on {school_tuple}")
        
        with lock:
                if school_name in saved_links:
                    continue

   

  

        q = f"{school_name} {state} website"
        url = f"https://www.google.com/search?q={q.replace(' ', '+')}"
        print(f"Following link: {url}")
        driver.get(url)

        if check_for_captcha(driver):
            time.sleep(60)

        try:
            wait = WebDriverWait(driver, 10)
            results = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="yuRUbf"]//a')))
            result = results[0]
            school_link = result.get_attribute('href')

            with lock:
                result_queue.append((school_name, school_link))
                save_school_links(result_queue)
                saved_links[school_name] = school_link
        
        except Exception as e:
            print(f"Error for {school_name} {state}: {e}")
        
     

    driver.quit()
 

## makes new webdriver to avoid captcha
def wbdvr_maker(position, size=(800, 600)):
    ua = UserAgent()
    user_agent = ua.random
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument('--headless')
    options.add_argument(f'--window-position={position[0]},{position[1]}')
    options.add_argument(f'--window-size={size[0]},{size[1]}')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def check_for_captcha(driver):
    current_url = driver.current_url
    if "sorry/index?continue" in current_url:
        print(f"Captcha encountered")
        return True
    else:
        return False

## iteratively saves the school links to the school links csv file as the code works
def save_school_links(school_links, file_path='school_links.csv'):
    df_links = pd.DataFrame(school_links, columns=['School Name', 'School Link'])
    if os.path.exists(file_path):
        df_existing = pd.read_csv(file_path)
        df_links = pd.concat([df_existing, df_links]).drop_duplicates(subset=['School Name']).reset_index(drop=True)
    df_links.to_csv(file_path, index=False)


## loads the csv file created by the get_school_links function, if it exists
def load_school_links(file_path='school_links.csv'): 
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        saved_links = {row['School Name']: row['School Link'] for _, row in df.iterrows()}
        return saved_links
    else:
        print(f"No saved school links found at {file_path}")
        return {}


def main():
    
    ## where the dados2 file is located on the machine
    folder_path = '/Users/johnreinker/Desktop/dados2'

    ## checks for school tuple csv, if it does not exist, calls process_csvs
    school_tuples = load_school_tuples()
    if school_tuples is None:
        school_tuples = process_csvs(folder_path)
    
    ## school_tuples = [('Saint Louis Priory School', 'Missouri'), ('St. Ignatius College Preparatory', 'California'), ('Crespi Carmelite', 'California')]
    ## checks for school links csv, if it does not exist, calls get_school_links
    saved_links = load_school_links()
    result_queue = []
    positions = [(0,0), (800,0),(0,600), (800,600) ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(get_school_links, school_tuples, saved_links, result_queue, positions[i])
            for i in range(4)
        ]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Exception: {e}")

    

  #  new_links = get_school_links(school_tuples, saved_links, result_queue)


if __name__ == "__main__":
    main()