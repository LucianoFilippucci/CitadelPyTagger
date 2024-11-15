from typing import List

class Track:
    def __init__(self, name, duration, artist_name, album_title, track_number, track_published ,artist_mbid=None, spotify_track_id = None):
            self.name = name
            self.duration = duration
            self.album_title = album_title
            self.artist_mbid = artist_mbid
            self.artist_name = artist_name
            self.track_number = track_number
            self.track_published = track_published
            self.spotify_track_id = spotify_track_id
    
    def get_name(self):
          return self.name
    
    def get_spotify_track_id(self):
          return self.spotify_track_id
    
    def get_track_number(self):
          return self.track_number
    
    def get_track_published(self):
          return self.track_published
    
    def get_artist(self):
          return self.artist_name
    
    def get_duration(self):
          return self.duration
    
    def get_album_title(self):
          return self.album_title
    
    def get_artist_mbid(self):
          return self.artist_mbid