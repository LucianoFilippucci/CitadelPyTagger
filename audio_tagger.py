from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, TRCK, TDRC
import os
import argparse
from pathlib import Path
import requests
import json
from dotenv import load_dotenv
from Artist import Artist
from Album import Album
from Track import Track
from datetime import datetime

load_dotenv()


def search_artist(artist_name) -> Artist:
    params = {
            'method': 'artist.getinfo',
            'artist': artist_name,
            'api_key': os.getenv("LASTFM_API_KEY"),
            'format': 'json'
        }
    response = requests.get(os.getenv("LASTFM_API_URL"), params = params)
    if response.status_code == 200:
        pretty_json = json.dumps(response.json(), indent = 4)
        with open('artist_response.json', 'w') as file:
            file.write(pretty_json)
        
        tags = [tag["name"] for tag in response['artist']['tags']['tag']]

        return Artist(
            name = response['artist']['name'],
            mbid = response['artist']['mbid'],
            tags= tags
        )

def retrive_image_from_musicbrainz(img_url, type):
    URL = os.getenv("MUSICBRAINZ_API_URL")

    match type:
        case "artist":
            URL += "artist/"
        case "track":
            URL += ""
        case "album":
            URL += ""
    
    params = {
        'query': '',
        'fmt': 'json'
    }

    headers  = {
        "User-Agent": os.getenv("USER_AGENT")
    }

    response = requests.get(URL, params= params, headers= headers)

    if response.status_code == 200:
        data = response.json()


def search_artist_song(artist_name, song_name) -> Track:
    # URI = LASTFM_API_URL + "?method=artist.getinfo&artist=Cher&api_key=YOUR_API_KEY&format=json"
    params = {
        'method': 'track.getinfo',
        'artist': artist_name,
        'track': song_name,
        'api_key': os.getenv("LASTFM_API_KEY"),
        'format': 'json'
    }

    

    response = requests.get(os.getenv("LASTFM_API_URL"), params = params)
    if response.status_code == 200:
        pretty_json = json.dumps(response.json(), indent = 4)
        with open('track_response.json', 'w') as file:
            file.write(pretty_json)
        
        # artist_mbid = response.json()['track']['artist']['mbid'] if  response.json()['track']['artist']['mbid'] else None
        artist_mbid = response.json().get('track', {}).get('artist', {}).get('mbid', None)
        album = search_album(
            album_name = response.json()['track']['album']['title'],
            album_artist = response.json()['track']['artist']['name']
        )    

        date_object = datetime.strptime(album.get_published, "%d %b %Y, %H:%M")
        formatted_date = date_object.strftime("%Y-%m-%dT%H:%M:%S")


        return Track(
            name = response.json()['track']['name'],
            duration = response.json()['track']['duration'],
            album_title = response.json()['track']['album']['title'],
            artist_mbid = artist_mbid,
            artist_name = response.json()['track']['artist']['name'],
            track_number = get_track_index(response.json(), album.tracks),
            track_published = formatted_date
        )
        
        

        
    else:
        print(f"Error: {response.status_code}")

def get_track_index(response, album: Album):
    for index, track in enumerate(album.get_tracks):
            if track == response['track']['name']:
                return index;

def search_album(album_name=None, album_artist=None, album_mbid=None) -> Album:
    params = {
                'method': 'album.getinfo',
                'album': album_name,
                'api_key': os.getenv("LASTFM_API_KEY"),
                'format': 'json'
    }
    if album_artist:
        params['artist'] = album_artist
        response = requests.get(os.getenv("LASTFM_API_URL"), params = params)
        if response.status_code == 200:
            pretty_json = json.dumps(response.json(), indent = 4)
            with open('album_response.json', 'w') as file:
                file.write(pretty_json)
            
            track_list = [track["name"] for track in response.json()['album']['tracks']['track']]

            return Album(
                name = response.json()['album']['name'],
                artist = response.json()['album']['artist'],
                tracks = track_list,
                published = response.json()['album']['wiki']['published'],
                album_mbid = response.json()['album']['mbid'] if response.json()['album']['mbid'] else None
            )
    


def tagger(directory):
    dir = Path(directory)
    file_count = sum(1 for f in dir.iterdir() if f.is_file())
    for entry in dir.iterdir():
        if entry.is_file():
            # audio = MP3(entry)
            # print(f"audio title: {audio.get('TIT2')}")
            # print(f"You're editing the song: {entry.name}")
            # song_title = input("Title (blank for default): ")
            # if song_title: 
            #     audio['TIT2'] = TIT2(encoding=3, text = song_title)
            
            # song_artist = input("Artist (leave blank for default): ")
            # if song_artist:
            #     audio['TPE1'] = TPE1(encoding=3, text = song_artist)
            
            # song_album = input("Album Name (blank for default): ")
            # if song_album:
            #     audio['TALB'] = TALB(encoding = 3, text = song_album)
            
            # song_genre = input("Song Genre (blank for default): ")
            # if song_genre:
            #     audio['TCON'] = TCON(encoding = 3, text = song_genre)
            # audio.save()
            # return
            audio = MP3(entry)
            print(f"Editing: {entry.name}")
            song_name = ""
            while not song_name:
                song_name = input("Track Name: ")
            artist_name = input("Artist Name: ")
            while not artist_name:
                artist_name = input("Artist Name: ")
            
            track = search_artist_song(artist_name, song_name)
            if track:
                audio['TIT2'] = TIT2(encoding = 3, text = track.get_name)
                audio['TPE1'] = TPE1(encoding = 3, text = track.get_artist)
                audio['TALB'] = TALB(encoding = 3, text = track.get_album_title)
                audio['TRCK'] = TRCK(encoding = 3, text = [f"{track.get_track_number}"])
                audio['TDRC'] = TDRC(encoding = 3, text = track.get_published)
                print("================================================================")
                for tag in audio.keys():
                    print(f"{tag}: {audio[tag]}")
                print("================================================================")
                audio.save()
                # TODO: an Else to log the track's that couldn't be tagged


    print(f"Number of files: {file_count}")

def search_artist_MUSICBRAINZ(artist_name) -> str:
    URI =  os.getenv("") + "artist/"
    params = {
        'query': artist_name,
        'fmt': 'json'
    }

    print(f"URI: {URI}")

    response = requests.get(URI, params=params)

    if response.status_code == 200:
        data = response.json()
        artists = data.get('artists', [])
        if artists:
            
            for index, artist in enumerate(artists, start = 0):
                print(f"SELECTION ID: {index}")
                print(f"Artist: {artist['name']}")
                print(f"ID: {artist['id']}")
                print(f"Disambiguation: {artist.get('disambiguation', 'N/A')}")
                print("-------------------------------------------------------")
        else:
            print("No artists found.")
            return ""
        selection = int(input("Which Artist do you Want: "))
        return artists[selection]['id']
    else:
        print(f"Error: {response}")
        return ""

    

def main():
    parser = argparse.ArgumentParser(description="a script to demonstrate argparse")

    parser.add_argument("-d", "--directory", type = str, default = "./",help = "The directory")
    parser.add_argument("-sa", "--search-artist", type=str, default= "", help = "Search for Artist Name")
    parser.add_argument("-sn", "--song-name", type = str, default = "", help = "Search for Artist Song")
    parser.add_argument("-sA", "--search-album", type = str, default = "", help= "Search for Album")

    args = parser.parse_args()

    if args.directory:
        tagger(args.directory)

    if args.search_artist and args.song_name:
        # artist_name = input("Artist Name: ")
        print(f"Track to find: {args.song_name} of Artist {args.search_artist}")
        track = search_artist_song(args.search_artist, args.song_name)

        print(f"Name: {track.name}")
        print(f"Album: {track.album_title}")
        print(f"Artist: {track.artist_name}")
    elif args.search_album and args.search_artist:
        print(f"Album to find: {args.search_album} of Artist {args.search_artist}")
        search_album(args.search_album, args.search_artist)
    elif args.search_artist:
        print(f"Searching artist: {args.search_artist}")
        search_artist(args.search_artist)


    



if __name__ == "__main__":
    main()