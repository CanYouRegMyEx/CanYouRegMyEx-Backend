import re
from enum import Enum, auto

class Profile:
    def __init__(
            self, 
            name_eng, 
            surname_eng, 
            name_jpn, 
            surname_jpn, 
            gender, 
            height, 
            weight, 
            occupations, 
            jp_voices, 
            eng_voices, 
            drama_actors
        ):

        self.name_eng = name_eng
        self.surname_eng = surname_eng
        self.name_jpn = name_jpn
        self.surname_jpn = surname_jpn
        self.gender = gender
        self.height = height
        self.weight = weight
        # self.statuses = # Alive/Dead, for factual and sometimes as perceived from another party
        self.occupations = occupations
        self.jp_voices = jp_voices
        self.eng_voices = eng_voices
        self.drama_actors = drama_actors

def extract_character(url):
    pass