import os
from dotenv import load_dotenv, set_key
from Artist import Artist
from Track import Track
import requests
import json
from datetime import datetime
from Album import Album
import logging
import time
from Exceptions.TokenExpiredException import TokenExpiredException

logging.basicConfig(
    level=logging.INFO,
    filename= "logs/spotify_service.log",
    format= "%(asctime)s - %(levelname)s - %(message)s",
    )

load_dotenv()

class SpotifyToken:
    __access_token = None
    __token_type = None
    __expires_in = None
    __scope = None
    __refresh_token = None

    def __init__(self) -> None:

        pass

    @classmethod
    def set_token(cls, access_token: str, token_type: str, expires_in: str, scope: str = None, refresh_token: str = None) -> None:
        cls.__access_token = access_token
        cls.__token_type = token_type
        cls.__expires_in = expires_in
        cls.__scope = scope
        cls.__refresh_token = refresh_token

    @classmethod
    def get_token(cls) -> dict:
        return {
            "access_token": cls.__access_token,
            "token_type": cls.__token_type,
            "expires_in": cls.__expires_in,
            "scope": cls.__scope,
            "refresh_token": cls.__refresh_token
        }
    

class Spotify:
    def __init__(self) -> None:
        self.request_token(False)
        pass   

    #if return true the token was requested again, if false then is retrieved from the .env
    def request_token(self, refresh: bool) -> bool:
        
        if os.getenv("SPOTIFY_ACCESS_TOKEN") and not refresh:
            SpotifyToken.set_token(
                os.getenv("SPOTIFY_ACCESS_TOKEN"),
                os.getenv("SPOTIFY_TOKEN_TYPE"),
                os.getenv("SPOTIFY_TOKEN_EXPIRATION"),
                os.getenv("SPOTIFY_TOKEN_SCOPE"),
                os.getenv("SPOTIFY_TOKEN_REFRESH_TOKEN")
            )
            return False
        else:
            headers = {
                "Content-Type":"application/x-www-form-urlencoded"
            }
            data = {
                "grant_type":"client_credentials"
            }

            # Commented since refresh_token is present only when using authorized api.
            # if refresh:
            #     data["refresh_token"] = SpotifyToken.get_token()["refresh_token"]
            # else:
            data["client_id"] = os.getenv("SPOTIFY_CLIENT_ID")
            data["client_secret"] = os.getenv("SPOTIFY_CLIENT_SECRET")

            response = requests.post(os.getenv("SPOTIFY_ACCESS_TOKEN_URL"), headers= headers, data= data)
            if response.status_code == 200:
                with open('response/Spotify/token.json', 'w') as file:
                    file.write(json.dumps(response.json(), indent = 4))
                SpotifyToken.set_token(
                    response.json()["access_token"],
                    response.json()["token_type"],
                    response.json()["expires_in"],
                    ## response.json()["scope"],
                    ## response.json()["refresh_token"]
                )

                ## DEV_ONLY
                set_key(".env", 'SPOTIFY_ACCESS_TOKEN', SpotifyToken.get_token()['access_token'])
                set_key(".env", 'SPOTIFY_TOKEN_TYPE', SpotifyToken.get_token()['token_type'])
                set_key(".env", 'SPOTIFY_TOKEN_EXPIRATION', str(SpotifyToken.get_token()['expires_in']))
                #set_key(".env", 'SPOTIFY_TOKEN_SCOPE', SpotifyToken.get_token()['scope'])
                #set_key(".env", 'SPOTIFY_TOKEN_REFRESH_TOKEN', SpotifyToken.get_token()['refresh_token'])
            return True

            
        
    def search_artist(self, artist_name: str) -> Artist:
        response = None
        try:
            response = self.get_request(
                "search",
                f"artist:{artist_name}",
                "artist",
                1
            )
        except TokenExpiredException as t:
            if self.request_token(True):
                response = self.get_request(
                    "search",
                    artist_name,
                    "artist",
                    1
                )
        with open('response/Spotify/artist.json', 'w') as file:
            file.write(json.dumps(response, indent = 4))
        return Artist(
            response["items"][0]["name"],
            response["items"][0]["genres"],
            spotify_id= response["items"][0]["id"]
        )    

    def search_track(self, track_name: str, artist_name: str):
        response = None
        try:
            response = self.get_request(
                "search",
                f"track:{track_name} artist:{artist_name}",
                "track",
                1
            )
        except TokenExpiredException as t:
            if self.request_token(True):
                response = self.get_request(
                "search",
                f"track:{track_name} artist:{artist_name}",
                "track",
                1
            )
        with open('response/Spotify/track.json', 'w') as file:
            file.write(json.dumps(response, indent = 4))
            
        
        album = Album(
            response["tracks"]["items"][0]["album"]["name"],
            response["tracks"]["items"][0]["artists"][0]["name"],
            response["tracks"]["items"][0]["album"]["total_tracks"], ##TODO: should change that, because it expect a dict of track names.
            response["tracks"]["items"][0]["album"]["release_date"],
            None,
            response["tracks"]["items"][0]["album"]["id"]
        )

       
        track = Track(
            response["tracks"]["items"][0]["name"],
            response["tracks"]["items"][0]["duration_ms"],
            response["tracks"]["items"][0]["artists"][0]["name"],
            album.get_name(),
            response["tracks"]["items"][0]["track_number"],
            album.get_published(),
            None,
            response["tracks"]["items"][0]["id"]
        )
        return track, album
        pass
    # requestEndpoint should be of type album/ or search etc... based on spotify request endopoint
    # query is the value to search ( for example BLACKPINK ), for simplicity, just for now, the passed query shopuld be of the form:
    # {type}:{value}. Asking the caller to format the query like this, will help if we need to narrow down the results with more filters. For example:
    # the search_track might want to narrow down to the song that is of that one artist. the query will look like:
    # track:Spicy artist:AESPA
    # but search_artist doesn't need that fine graned filtering, and it will pass only artist:AESPA
    # type is the type, in this case artists (can be artist, track, album, playlist etc...)
    # limit is how many results we want
    def get_request(self, requestEndpoint: str, query: str, type: str, limit: int) -> json:
        url = os.getenv("SPOTIFY_BASE_API_URL") + requestEndpoint
        headers = {
            "Authorization": f"Bearer {SpotifyToken.get_token()["access_token"]}"
        }

        params = {
            "q": query,
            "type": type,
            "limit": limit
        }

        response = requests.get(url, headers= headers, params= params)

        match response.status_code:
            case 200:
                return response.json()
            case 401:
                logging.error(f"Unauthorized (401): Invalid or expired access token.")
                # TODO: refresh the token and retry
                raise TokenExpiredException("Token is invalid or expired")
                pass
            case 403:
                logging.error(f"Forbidden (403): Bad OAuth request.")
                #TODO: idk
                pass
            case 429:
                logging.error(f"Rate Limit Exceeded. Error Message: {response.json()["message"]}")
                #TODO: idk
                pass
            case _:
                logging.error(f"Unexpected response code (status code: {response.json()["status"]}) message: {response.json()["message"]}")
        pass