import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
import pandas as pd


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

    return school_tuples






def search_for_channel(yt, school_name, state):
    response = yt.search().list(
        q=f"{school_name} {state}",
        part='snippet',
        type='channel',
        maxResults=1
    ).execute()

    items = response.get('items', [])
    if not items:
        return None
    
    item = items[0]
    info = {
        'title': item['snippet']['title'],
        'id': item['snippet']['channelId']
    }

    return info


def main():
    '''
    folder_path = '/Users/johnreinker/Desktop/dados2'
    school_tuples = process_csvs(folder_path)
    '''
    
    school_tuples = [('Saint Louis Priory School', 'Missouri')]
    
    load_dotenv()
    API_KEY = os.getenv('API_KEY')
    yt = build('youtube', 'v3', developerKey=API_KEY)


    for school_tuple in school_tuples:
        school_name, state = school_tuple

        try:
            info = search_for_channel(yt, school_name, state)
            if info:
                print(f'Found info for {school_name}, {state}: {info}')
            else:
                print(f'No info for {school_name}, {state}')

        except Exception as e:
            print(f"An error occurred while searching for channel for {school_name}, {state}: {e}")

    return info



