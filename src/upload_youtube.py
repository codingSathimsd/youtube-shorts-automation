from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import os

def get_youtube_client():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
        client_id=os.environ["YOUTUBE_CLIENT_ID"],
        client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token"
    )
    return build('youtube', 'v3', credentials=creds)

def upload_short(clip_path, metadata):
    youtube = get_youtube_client()
    title = metadata['title'] + " #Shorts"
    description = metadata['description'] + "\n\n" + metadata['hashtags']

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': metadata['tags'] + ['Shorts', 'viral', 'trending'],
            'categoryId': '22',
            'defaultLanguage': 'en'
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }

    media = MediaFileUpload(
        clip_path,
        mimetype='video/mp4',
        resumable=True,
        chunksize=1024 * 1024
    )

    print(f"Uploading: {title}")
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )
    response = request.execute()
    video_id = response['id']
    print(f"Uploaded: https://youtube.com/shorts/{video_id}")
    return video_id
