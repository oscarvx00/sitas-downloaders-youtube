import requests
import os
import urllib.parse

YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']



def search_song(song_name : str):

    url = "https://www.googleapis.com/youtube/v3/search?key=AIzaSyCXSyAhli8w0E1o5dGeUylVtEkiSpdedrI&part=id&q=" + urllib.parse.quote(song_name)

    response = requests.get(url=url)
    response_data = response.json()

    try:
        return response_data['items'][0]['id']['videoId']
    except:
        return None
    
