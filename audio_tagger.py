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
from DataService.Spotify import Spotify
import logging


load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    filename= "logs/app.log",
    format= "%(asctime)s - %(levelname)s - %(message)s",
    )


def tagger(directory, data_service):
    dir = Path(directory)
    file_count = sum(1 for f in dir.iterdir() if f.is_file())
    print(f"Found {file_count} files in the given directory.\n")

    for entry in dir.iterdir():
        if entry.is_file():
            audio = MP3(entry)
            print(f"Editing: {entry.name}")
            song_name = ""
            while not song_name:
                song_name = input("Track Name: ")
            if(song_name[0] == "-" and song_name[1] == "s"):
                print(f"Skipping {entry.name}")
                print("========================================================")
                continue
            artist_name = input("Artist Name: ")
            while not artist_name:
                artist_name = input("Artist Name: ")

            metadata_service = None
            match data_service:
                case "spotify":
                    metadata_service = Spotify()
                case _:
                    logging.error(f"Invalid Data Service: {data_service}")
                    print("An Error Occurred Check app.log.")
                    exit -1

            track, album = metadata_service.search_track(song_name, artist_name)
            if track:
                audio['TIT2'] = TIT2(encoding = 3, text = track.get_name())
                audio['TPE1'] = TPE1(encoding = 3, text = track.get_artist())
                audio['TALB'] = TALB(encoding = 3, text = track.get_album_title())
                audio['TRCK'] = TRCK(encoding = 3, text = [f"{track.get_track_number()}"])
                audio['TDRC'] = TDRC(encoding = 3, text = track.get_track_published())
                print("================================================================")
                for tag in audio.keys():
                    print(f"{tag}: {audio[tag]}")
                print("================================================================")
                audio.save()
                new_name = f"{track.get_artist()} - {track.get_name()}" + entry.suffix
                new_file_path = entry.parent  / new_name
                entry.rename(new_file_path)
                # TODO: an Else to log the track's that couldn't be tagged



    
def main():
    parser = argparse.ArgumentParser(description="a script to demonstrate argparse")

    parser.add_argument("-d", "--directory", type = str, default = "./",help = "The directory")
    parser.add_argument("-sa", "--search-artist", type=str, default= "", help = "Search for Artist Name")
    parser.add_argument("-sn", "--song-name", type = str, default = "", help = "Search for Artist Song")
    parser.add_argument("-sA", "--search-album", type = str, default = "", help= "Search for Album")
    parser.add_argument("--data-service", type= str, required= True, help= "Metadata Service: spotify, lastfm, musicbrainz")


    args = parser.parse_args()

    if args.directory:
        tagger(args.directory, args.data_service)

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