import time
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup

## load the school website links csv created by school_scrapper.py
def load_school_links(file_path='school_links.csv'):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        school_links = df['School Link'].tolist()
        return school_links
    else:
        print(f"No school link file found at {file_path}")
        return None

## uses html requests on the school website links to obtain html objects of a school website
def html_getter(school_links):
    html_contents = []

    for link in school_links:
        try:
            response = requests.get(link)
            response.raise_for_status()
            if response.text:
                html_contents.append(response.text)
            time.sleep(5)

        except requests.RequestException as e:
            print(f"Error fetching html contents for {link}: {e}")

    return html_contents

## parses the html objects obtained from html_getter, looking for youtube links
def html_parser(html_contents):
    youtube_links = []
    seen_links = set()
    for h in html_contents:
        soup = BeautifulSoup(h, 'html.parser')

        for tag in soup.find_all('a', href=True):
            href_content = tag['href']

            if "youtube.com" in href_content and href_content not in seen_links:
                youtube_links.append(href_content)
                seen_links.add(href_content)

    return youtube_links


def main():
    
    school_links = load_school_links()
    
   
    test_links = school_links[0:19]
    print(test_links)
    html_contents = html_getter(test_links)
    #html_contents = html_getter(school_links)
    youtube_links = html_parser(html_contents)
    print(youtube_links)

if __name__ == "__main__":
    main()