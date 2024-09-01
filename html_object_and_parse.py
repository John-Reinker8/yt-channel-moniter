import time
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup

## load the school website links csv created by school_scrapper.py
def load_school_links(file_path='school_links.csv'):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        school_links = list(zip(df['School Name'], df['State'], df['School Link']))
        return school_links
    else:
        print(f"No school link file found at {file_path}")
        return None
    
## loads the csv file of work done so far
def load_media(file_path='school_medias.csv'): 
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        links_done = set(df['School Link'].tolist())
        return links_done
    else:
        print(f"No done school links found at {file_path}")
        return set()

def save_media(name, state, link, youtube_link, twitter_link, instagram_link, facebook_link, output_file='school_medias.csv'):
    data = {
        'School Name': [name],
        'State': [state],
        'School Link': [link],
        'YouTube Link': [youtube_link],
        'Twitter / X Link': [twitter_link],
        'Instagram Link': [instagram_link],
        'Facebook Link': [facebook_link]
    }

    df = pd.DataFrame(data)

    if os.path.exists(output_file):
        df.to_csv(output_file, mode='a', header=False, index=False)
    else:
        df.to_csv(output_file, mode='w', header=True, index=False)

## uses html requests on the school website links to obtain html objects of a school website
def html_getter(school_links, links_done):
    for name, state, link in school_links:
        if link in links_done:
            continue

        print(f"Fetching html for: {link}")
        try:
            response = requests.get(link)
            response.raise_for_status()
            if response.text:
                youtube_link, twitter_link, instagram_link, facebook_link = html_parser(response.text)
                save_media(name, state, link, youtube_link, twitter_link, instagram_link, facebook_link)

        except requests.RequestException as e:
            print(f"Error fetching html contents for {link}: {e}")
        
    return

## parses the html objects obtained from html_getter, looking for youtube links
def html_parser(html_contents):
    youtube_link = ""
    twitter_link = ""
    instagram_link = ""
    facebook_link = ""
    
    for h in html_contents:
        soup = BeautifulSoup(h, 'html.parser')

        for tag in soup.find_all('a', href=True):
            href_content = tag['href']

            if "youtube.com" in href_content:
                youtube_link = href_content
        
            if "x.com" in href_content:
                twitter_link = href_content
            elif "twitter.com" in href_content:
                twitter_link = href_content
         
            if "instagram.com" in href_content:
                instagram_link = href_content
       
            if "facebook.com" in href_content:
                facebook_link = href_content
            
    return youtube_link, twitter_link, instagram_link, facebook_link


def main():
    start = time.time()
    school_links = load_school_links()
    links_done = load_media()
   
    test_links = school_links[0:5]
    
    html_getter(test_links, links_done)


    end = time.time()
    print(f"It took {end - start} sec to complete.")
if __name__ == "__main__":
    main()