
class Album:
    def __init__(self, name, artist, tracks, published, album_mbid=None, spotify_album_id = None):
        self.__name = name
        self.__artist = artist
        self.__tracks = tracks
        self.__published = published
        self.__album_mbid = album_mbid
        self.__spotify_album_id = spotify_album_id

    def get_name(self):
        return self.__name
    
    def get_spotify_album_id(self):
        return self.__spotify_album_id
    
    def get_artist(self):
        return self.__artist
    
    def get_tracks(self):
        return self.__tracks
    
    def get_published(self):
        return self.__published
    
    def get_album_mbid(self):
        return self.__album_mbid
        