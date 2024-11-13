from typing import List

class Track:
    def __init__(self, name, duration, artist_name, album_title, track_number, track_published ,artist_mbid=None):
            self.__name = name
            self.__duration = duration
            self.__album_title = album_title
            self.__artist_mbid = artist_mbid
            self.__artist_name = artist_name
            self.__track_number = track_number
            self.__track_published = track_published
    
    def get_name(self):
          return self.__name
    
    def get_track_number(self):
          return self.__track_number
    
    def get_track_published(self):
          return self.__track_published
    
    def get_artist(self):
          return self.__artist_name
    
    def get_duration(self):
          return self.__duration
    
    def get_album_title(self):
          return self.__album_title
    
    def get_artist_mbid(self):
          return self.__artist_mbid