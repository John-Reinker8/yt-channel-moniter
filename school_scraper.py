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

## load variables from .env
load_dotenv()
BRIGHTDATA_PROXY_USER = os.getenv('BRIGHTDATA_PROXY_USER')
BRIGHTDATA_PROXY_PASSWORD = os.getenv('BRIGHTDATA_PROXY_PASSWORD')
BRIGHTDATA_PROXY_ADDRESS = os.getenv('BRIGHTDATA_PROXY_ADDRESS')

## Used to configure proxies from BrightData
def get_proxy_options():
    proxy_options = {
        'proxyType': ProxyType.MANUAL,
        'httpProxy': f'http://{BRIGHTDATA_PROXY_USER}:{BRIGHTDATA_PROXY_PASSWORD}@{BRIGHTDATA_PROXY_ADDRESS}',
        'sslProxy': f'http://{BRIGHTDATA_PROXY_USER}:{BRIGHTDATA_PROXY_PASSWORD}@{BRIGHTDATA_PROXY_ADDRESS}',
    }
    return proxy_options


## extracts roughly 118k school and state pairs from dados2 file
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

    print(len(school_tuples))
    ## saves the 118k tuples to a csv file so we don't have to rerun this whole function
    df_tuples = pd.DataFrame(school_tuples, columns=['School Name', 'State'])
    df_tuples.to_csv('school_tuples.csv', index=False)

    return school_tuples

## loads the .csv file created by the process_csvs function, if it exists
def load_school_tuples(file_path='school_tuples.csv'): 
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        school_tuples = list(df.itertuples(index=False, name=None))
        return school_tuples
    else:
        print(f"No saved school tuples found at {file_path}")
        return None

## uses a webdriver and the list of school, state pairs to obtain the school website links
def get_school_links(school_tuples, saved_links):

    new_links = []
    driver = wbdvr_maker()
    i = 0

    for school_name, state in school_tuples:

        if school_name in saved_links:
            continue
        
        if i >= 6:
            i = 0
            driver.quit()
            driver = wbdvr_maker()

        q = f"{school_name} {state} website"
        url = f"https://www.google.com/search?q={q.replace(' ', '+')}"
        print(f"Following link: {url}")
        driver.get(url)

        if check_for_captcha(driver) == True:
            time.sleep(30)

        try:
            random_mouse_movements(driver)
            random_scroll(driver)
            wait = WebDriverWait(driver, 10)
            results = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="yuRUbf"]//a')))
            result = results[0]
            school_link = result.get_attribute('href')
            new_links.append((school_name, school_link))
            saved_links[school_name] = school_link
            i += 1
        
        except Exception as e:
            print(f"Error for {school_name} {state}: {e}")
            i += 1
            continue


        save_school_links(new_links)
        time.sleep(5)

    driver.quit()
    return new_links

## makes new webdriver to avoid captcha
def wbdvr_maker():
    ua = UserAgent()
    user_agent = ua.random
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
  ##  options.add_argument('--headless')
    proxy_options = get_proxy_options()
    proxy = Proxy(proxy_options)
    options.Proxy = proxy
    options.add_arguement('--proxy-server=%s' % proxy_options['httpProxy'])

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver
     
def random_scroll(driver):
    for _ in range(random.randint(3, 7)):
        scroll_height = random.randint(100, 500)
        driver.execute_script(f"window.scrollBy(0, {scroll_height});")
        time.sleep(random.uniform(0.5, 1.5))

def random_mouse_movements(driver):
    action = ActionChains(driver)
    window_size = driver.get_window_size()
    window_width = window_size['width']
    window_height = window_size['height']

    for _ in range(random.randint(5, 10)):
        x_offset = random.randint(0, window_width // 2)
        y_offset = random.randint(0, window_height // 2)
        x_direction = random.choice([-1, 1])
        y_direction = random.choice([-1, 1])

        x_offset *= x_direction
        y_offset *= y_direction

        # Ensure the target is within bounds
        target_x = max(0, min(window_width, x_offset))
        target_y = max(0, min(window_height, y_offset))

        action.move_by_offset(target_x, target_y).perform()
        time.sleep(random.uniform(0.1, 0.5))
        action.move_by_offset(-target_x, -target_y).perform() 

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
    new_links = get_school_links(school_tuples, saved_links)


if __name__ == "__main__":
    main()