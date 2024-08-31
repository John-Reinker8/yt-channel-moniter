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
    count = 0
    for link in school_links:
        print(f"{count} Fetching html for: {link}")
        try:
            response = requests.get(link)
            response.raise_for_status()
            if response.text:
                html_contents.append(response.text)
          ##  time.sleep(5)

        except requests.RequestException as e:
            print(f"Error fetching html contents for {link}: {e}")

        count += 1

    return html_contents

## parses the html objects obtained from html_getter, looking for youtube links
def html_parser(html_contents):
    youtube_links = []
    twitter_links = []
    instagram_links = []
    facebook_links = []
    seen_links = set()

    for h in html_contents:
        soup = BeautifulSoup(h, 'html.parser')

        for tag in soup.find_all('a', href=True):
            href_content = tag['href']

            if "youtube.com" in href_content and href_content not in seen_links:
                youtube_links.append(href_content)
        
            if "x.com" in href_content and href_content not in seen_links:
                twitter_links.append(href_content)
            elif "twitter.com" in href_content and href_content not in seen_links:
                twitter_links.append(href_content)
         
            if "instagram.com" in href_content and href_content not in seen_links:
                instagram_links.append(href_content)
       
            if "facebook.com" in href_content and href_content not in seen_links:
                facebook_links.append(href_content)
            
            seen_links.add(href_content)

    return youtube_links, twitter_links, instagram_links, facebook_links


def main():
    start = time.time()
    school_links = load_school_links()
    
   
    test_links = school_links[0:5]
    print(test_links)
    html_contents = html_getter(test_links)
    #html_contents = html_getter(school_links)
    youtube_links,twitter_links, instagram_links, facebook_links = html_parser(html_contents)
    print(youtube_links)
    print(twitter_links)
    print(instagram_links)
    print(facebook_links)
    end = time.time()

    print(f"It took {end - start} sec to complete.")
if __name__ == "__main__":
    main()