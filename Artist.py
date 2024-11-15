from typing import List

class Artist:
    def __init__(self, name, tags, mbid=None, image=None, spotify_id = None):
        self.name = name
        self.mbid = mbid
        self.image = image
        self.tags = tags
        self.spotify_id = spotify_id
    
    def get_name(self) -> str:
        return self.name
    
    def get_spotify_id(self) -> str:
        return self.spotify_id

    def get_tags(self) -> List[str]:
        return self.tags
    
    def get_mbid(self) -> str:
        return self.mbid
    
    def get_image(self) -> str:
        return self.image
    

    