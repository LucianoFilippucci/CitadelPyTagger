import os
from dotenv import load_dotenv
from Artist import Artist
from Track import Track
import requests
import json
from datetime import datetime
from Album import Album

load_dotenv()

class LastFM:
    __LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
    __LASTMF_API_URL = os.getenv("LASTFM_API_URL")

    def __init__(self):
        pass

    def get_artist(self, artist_name: str) -> Artist:
        params = {
            'method': 'artist.getinfo',
            'artist': artist_name,
            'api_key': self.__LASTFM_API_KEY,
            'format': 'json'
        }

        response = requests.get(url = self.__LASTMF_API_URL, params = params)
        if response.status_code == 200:
            # json_response = json.dumps(response.json(), indent = 4)
            
            tags = [tag["name"] for tag in response['artist']['tags']['tag']]
            return Artist(
                name = response['artist']['name'],
                mbid = response['artist']['mbid'],
                tags= tags
            )
        return None
    
    def get_song(self, song_name: str, artist_name: str = None ) -> Track:
        params = {
            'method': 'track.getinfo',
            'track': song_name,
            'api_key': self.__LASTFM_API_KEY,
            'format': 'json'
        }

        response = requests.get(url= self.__LASTMF_API_URL, params = params)
        if response.status_code == 200:
            artist = self.get_artist(artist_name if artist_name else response.json()['track']['artist']['name'])
            album = self.search_album(
                album_name = response.json()['track']['album']['title'],
                album_artist = artist.get_name
            )
            date_object = datetime.strptime(album.get_published, "%d %b %Y, %H:%M")
            formatted_date = date_object.strftime("%Y-%m-%dT%H:%M:%S")

            return Track(
                name = response.json()['track']['name'],
                duration = response.json()['track']['duration'],
                album_title = album.get_name,
                artist_mbid = artist.get_mbid if artist.get_mbid else response.json().get('track', {}).get('artist', {}).get('mbid', None),
                artist_name = response.json()['track']['artist']['name'],
                track_number = self.get_track_index(response.json()['track']['name'], album.tracks),
                track_published = formatted_date
            )
    
    def get_track_index(self, track_name:str , album: Album):
        for index, track in enumerate(album.get_tracks):
                if track == track_name:
                    return index + 1;
    
    def search_album(self, album_name=None, album_artist=None, album_mbid=None) -> Album:
        params = {
                    'method': 'album.getinfo',
                    'album': album_name,
                    'api_key': self.__LASTFM_API_KEY,
                    'format': 'json'
        }
        if album_artist:
            params['artist'] = album_artist
            response = requests.get(self.__LASTMF_API_URL, params = params)
            if response.status_code == 200:
                pretty_json = json.dumps(response.json(), indent = 4)
                # with open('album_response.json', 'w') as file:
                #     file.write(pretty_json)
                
                track_list = [track["name"] for track in response.json()['album']['tracks']['track']]

                return Album(
                    name = response.json()['album']['name'],
                    artist = response.json()['album']['artist'],
                    tracks = track_list,
                    published = response.json()['album']['wiki']['published'],
                    album_mbid = response.json()['album']['mbid'] if response.json()['album']['mbid'] else None
                )