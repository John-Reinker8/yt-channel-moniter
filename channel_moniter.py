import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
import channel_finder as cf

def get_Videos(yt, channel_id):

    channel_object = yt.channels().list(
        part='contentDetails',
        id=channel_id
    ).execute()
    
    uploads_list_id = channel_object['items'][0]['contentDetails']['relatedPlaylists']['uploads']


    video_ids = []
    video_titles = []
    next_page = None

    while True:
        uploads = yt.playlistItems().list(
            part='contentDetails',
            playlistId=uploads_list_id,
            maxResults=50,
            pageToken=next_page
        ).execute()

        next_page = uploads.get('nextPageToken')
       
        for item in uploads['items']:
            video_ids.append(item['contentDetails']['videoId'])

        if not next_page:
            break


    for id in video_ids:
        video_object = yt.videos().list(
            part='snippet,status',
            id=id
        ).execute()

        if video_object['items'][0]['status']['uploadStatus'] == 'processed':
            video_titles.append(video_object['items'][0]['snippet']['title'])

    return video_titles


def main():
    load_dotenv()
    API_KEY = os.getenv('API_KEY')

    yt = build('youtube', 'v3', developerKey=API_KEY)

    info = cf.main() ## get the channel title and id from channel_finder script
    channel_title = info['title']
    channel_id = info['id']

    try:
        videos = get_Videos(yt, channel_id)
    except Exception as e:
        print(f'Error in requesting channel videos: {e}')

    print(f'Results for {channel_title}: ')
    print(videos[0])
    print(videos[-1])
    print(len(videos))



main()


## look into batch requests