import os
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup

def x_links_cleaner(df):
    valid_x_link_pattern = r'^(https?://)?(www\.)?x\.com(/.*)?$'
    count = 0
    
    # Iterate over the 'Twitter / X Link' column to find and delete invalid links
    for index, row in df.iterrows():
        x_link = row['Twitter / X Link']
        
        # Handle NaN values by converting them to an empty string
        if pd.isna(x_link):
            x_link = ""
        
        # Check if "x.com" is in the link and it does not match the valid pattern
        if "x.com" in x_link and not re.match(valid_x_link_pattern, x_link):
            count += 1
            print(f"Deleting invalid x_link: {row['School Name']}, {row['State']}, {x_link}")
            
            # Set the cell value to empty
            df.at[index, 'Twitter / X Link'] = ""

            new_x_link = fetch_valid_x_link(row['School Link'])
            if new_x_link:
                df.at[index, 'Twitter / X Link'] = new_x_link 

    print(f"Total invalid x_links deleted: {count}")
    return df

def fetch_valid_x_link(school_link):
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
        "//twitter.com", "//instagram.com",
        "//youtube.com", "//facebook.com",
        "//x.com",
    }
     
    try:
        print(f"Fetching {school_link} for a valid x.com link...")
        response = requests.get(school_link, timeout=10)
        response.raise_for_status()

        # Parse the HTML content to find x.com links
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup.find_all('a', href=True):
            href_content = tag['href']
            if "x.com" in href_content and re.match(r'^(https?://)?(www\.)?x\.com(/.*)?$', href_content):
                if href_content.rstrip('/') not in base_urls:
                    print(f"Found for {school_link}")
                    return href_content
            elif "twitter.com" in href_content:
                if href_content.rstrip('/') not in base_urls:
                    print(f"Found for {school_link}")
                    return href_content

    except requests.RequestException as e:
        print(f"Error fetching {school_link}: {e}")
    except Exception as e:
        print(f"Error while processing {school_link}: {e}")
    
    return None  # Return None if no valid link is found
                                        



def load_file(file_path='school_medias.csv'):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df
    else:
        print("Error: File not found")
        return None

def main():
    ##yt_links, x_links, insta_links, fb_links = load_file()
    df = load_file()

    df_cleaned = x_links_cleaner(df)
    df_cleaned.to_csv('school_medias.csv', index=False)


main()