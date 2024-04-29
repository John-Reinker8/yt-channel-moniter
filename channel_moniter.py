import os
from dotenv import load_dotenv
from googleapiclient.discovery import build


def parse_URL(channel_url):

    code = ''
    is_username = False

    pos = channel_url.find('/user/')
    if pos != -1:
        code = channel_url[(pos + 6):]
        is_username = True

    else:
        pos = channel_url.find('/channel/')
        if pos != -1:
            code = channel_url[(pos + 9):]

        else:
            print('Parse failed')
            exit()

    return code, is_username


def get_Videos(yt, code, is_username):

    if is_username:
        channel_object = yt.channels().list(
            part='contentDetails',
            forUsername=code
        ).execute()
    else:
        channel_object = yt.channels().list(
            part='contentDetails',
            id=code
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

    channel_url = ''
    
 
    code, is_username = parse_URL(channel_url)

    videos = get_Videos(yt, code, is_username)

    for v in videos:
        print(v)

    print(len(videos))



main()


## look into batch requests