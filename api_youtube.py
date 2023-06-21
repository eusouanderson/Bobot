from googleapiclient.discovery import build
import SECRET_KEY


def search_videos(query):
    youtube = build('youtube', 'v3', developerKey=SECRET_KEY.API_KEY)

    request = youtube.search().list(
        part='snippet', q=query, type='video', maxResults=1
    )
    response = request.execute()

    for item in response['items']:
        video_title = item['snippet']['title']
        video_author = item['snippet']['channelTitle']
        video_id = item['id']['videoId']
        video_link = f'https://www.youtube.com/watch?v={video_id}'

    return video_title, video_author, video_link
