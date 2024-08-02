from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import pandas as pd
from fake_useragent import UserAgent
import threading
import concurrent.futures
from collections import deque
import urllib.parse

## globals
lock = threading.Lock()
active_threads = []
max_threads = 4

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

## loads the csv file created by the get_school_links function, if it exists
def load_school_links(file_path='school_links.csv'): 
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        saved_links = {(row['School Name'], row['State']): row['School Link'] for _, row in df.iterrows()}
        return saved_links
    else:
        print(f"No saved school links found at {file_path}")
        return {}

## uses a webdriver and the list of school, state pairs to obtain the school website links
def get_school_links(school_tuples, saved_links, result_queue, position, id):
    try:
        driver = wbdvr_maker(position, id)
        while school_tuples:
            with lock:
                if not school_tuples:
                    break
                school_tuple = school_tuples.popleft()

            school_name, state = school_tuple
            
            with lock:
                    if (school_name, state) in saved_links:
                        continue

            q = f"{school_name} {state} website"
            parsed_q = urllib.parse.quote(q)
            url = f"https://www.google.com/search?q={parsed_q}"
            print(f"Thread {threading.current_thread().name} is working on {school_tuple}. Link: {url}\n")
            driver.get(url)

            if check_for_captcha(driver):
                input(f"Press Enter to continue for {id}\n")

            try:
                wait = WebDriverWait(driver, 10)
                xpaths = '//div[@class="yuRUbf"]//a | //div[@class="P8ujBc v5yQqb jqWpsc"]//a'
                
                results = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpaths)))

                if results:
                    result = results[0]
                    school_link = result.get_attribute('href')
        
                    if school_link:
                        with lock:
                            result_queue.append((school_name, state, school_link))
                            save_school_links(result_queue)
                            saved_links[(school_name, state)] = school_link
                    
                    else:
                        print('No link found')
            
            except Exception as e:
                print(f"Error in inner loop for {id}: {school_name} {state} : {e}")
                driver.quit()
                driver = wbdvr_maker(position, id)
            
    except Exception as e:
        print(f"Error in outer loop for {id}: {school_name} {state} : {e}")
        driver.quit()
        return
        
    driver.quit()
    return

## makes webdriver
def wbdvr_maker(position, id,  size=(800, 600)):
    try:
        ua = UserAgent()
        user_agent = ua.random
        options = webdriver.ChromeOptions()
        options.add_argument(f'user-agent={user_agent}')
        # options.add_argument('--headless')
        options.add_argument(f'--window-position={position[0]},{position[1]}')
        options.add_argument(f'--window-size={size[0]},{size[1]}')
        driver_path = '/Users/johnreinker/.wdm/drivers/chromedriver/mac64/126.0.6478.127/chromedriver-mac-x64/chromedriver'
        if not os.path.exists(driver_path):
            print(f"Downloading latest CD version")
            driver_path = ChromeDriverManager().install()
        driver = webdriver.Chrome(service=Service(driver_path), options=options)
        return driver
    except Exception as e:
        print(f"Error making WD for {id}: {e}")

def check_for_captcha(driver):
    current_url = driver.current_url
    if "sorry/index?continue" in current_url:
        return True
    else:
        return False

## iteratively saves the school links to the school links csv file as the code works
def save_school_links(school_links, file_path='school_links.csv'):
    df_links = pd.DataFrame(school_links, columns=['School Name', 'State', 'School Link'])
    if os.path.exists(file_path):
        df_existing = pd.read_csv(file_path)
        df_links = pd.concat([df_existing, df_links]).drop_duplicates(subset=['School Name', 'State']).reset_index(drop=True)
    df_links.to_csv(file_path, index=False)

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
    positions = [(0,0), (800,0),(0,600), (800,600)]

    ## sets up max_threads for parallel work, creates a new thread if one goes down
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        while school_tuples:
            with lock:
                if len(active_threads) < max_threads:
                    for id in range(max_threads):
                        if id not in active_threads:
                            active_threads.append(id)
                            executor.submit(get_school_links, school_tuples, saved_links, result_queue, positions[id], id)
    return

if __name__ == "__main__":
    main()