import os
import pandas as pd


def load_file(file_path='school_medias.csv'):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        yt_links = df['YouTube Link'].tolist()
        x_links = df['Twitter / X Link'].tolist()
        insta_links = df['Instagram Link'].tolist()
        fb_links = df['Facebook Link'].tolist()

        return yt_links, x_links, insta_links, fb_links
    
    else:
        print("Error")
        return None

def cleaner(links):
    unique_links = set()
    duplicates = []

    for link in links:

        if pd.isna(link): 
            continue
        if link in unique_links:
            duplicates.append(link)
        else:
            unique_links.add(link)

    return unique_links, duplicates

def main():
    yt_links, x_links, insta_links, fb_links = load_file()

    unique_yt_links, yt_dups = cleaner(yt_links)
    unique_x_links, x_dups = cleaner(x_links)
    unique_insta_links, insta_dups = cleaner(insta_links)
    unique_fb_links, fb_dups = cleaner(fb_links)

    print(f"YT: {len(unique_yt_links)}\n")
    print(f"YT dupes: {len(yt_dups)}\n")
    print(f"X: {len(unique_x_links)}\n")
    print(f"X dupes: {len(x_dups)}\n")
    print(f"Insta: {len(unique_insta_links)}\n")
    print(f"Insta dupes: {len(insta_dups)}\n")
    print(f"FB: {len(unique_fb_links)}\n")
    print(f"FB dupes: {len(fb_dups)}\n")
    
main()