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

## save the media links to the output file
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

        skip_domains = ['usnews.com', 'yelp.com', 'niche.com']
        if any(domain in link for domain in skip_domains):
            print(f"Skip {link}")
            save_media(name, state, link, youtube_link="", twitter_link="" , instagram_link="", facebook_link="")
            continue

        if 'facebook.com' in link:
            print(f"Skip fb {link}")
            save_media(name, state, link, youtube_link="", twitter_link="" , instagram_link="", facebook_link=link)
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
            save_media(name, state, link, youtube_link="", twitter_link="" , instagram_link="", facebook_link="")

    return

## parses the html objects obtained from html_getter, looking for youtube links
def html_parser(html_contents):
    youtube_link = ""
    twitter_link = ""
    instagram_link = ""
    facebook_link = ""
    soup = BeautifulSoup(html_contents, 'html.parser')
    base_urls = {
        "https://youtube.com", "http://youtube.com", 
        "https://www.youtube.com", "http://www.youtube.com",
        "https://twitter.com", "http://twitter.com", 
        "https://www.twitter.com", "http://www.twitter.com",
        "https://x.com", "http://x.com", 
        "https://www.x.com", "http://www.x.com",
        "https://instagram.com", "http://instagram.com", 
        "https://www.instagram.com", "http://www.instagram.com",
        "https://facebook.com", "http://facebook.com", 
        "https://www.facebook.com", "http://www.facebook.com",
        "https://wix.com", "http://wix.com", 
        "https://www.wix.com", "http://www.wix.com",
    }

    for tag in soup.find_all('a', href=True):
        href_content = tag['href']

        if "youtube.com" in href_content:
           if href_content.rstrip('/') not in base_urls:
                youtube_link = href_content
    
        if "x.com" in href_content or "twitter.com" in href_content:
            if href_content.rstrip('/') not in base_urls:
                twitter_link = href_content
        
        if "instagram.com" in href_content:
            if href_content.rstrip('/') not in base_urls:
                instagram_link = href_content
    
        if "facebook.com" in href_content:
            if href_content.rstrip('/') not in base_urls:
                facebook_link = href_content
            
    return youtube_link, twitter_link, instagram_link, facebook_link


def main():
    start = time.time()
    school_links = load_school_links()
    links_done = load_media()
   
    html_getter(school_links, links_done)

    end = time.time()
    print(f"It took {end - start} sec to complete.")
if __name__ == "__main__":
    main()