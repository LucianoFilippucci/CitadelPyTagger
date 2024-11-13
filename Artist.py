from typing import List

class Artist:
    def __init__(self, name, tags, mbid=None, image=None):
        self.name = name
        self.mbid = mbid
        self.image = image
        self.tags = tags
    
    def get_name(self) -> str:
        return self.name

    def get_tags(self) -> List[str]:
        return self.tags
    
    def get_mbid(self) -> str:
        return self.mbid
    
    def get_image(self) -> str:
        return self.image
    

    