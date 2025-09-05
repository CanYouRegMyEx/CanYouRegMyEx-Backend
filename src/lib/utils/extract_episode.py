import re

class MainCharacter:
    def __init__(
            self,
            character_url: str,
            character_image_url: str,
            name_eng: str,
            ):
        
        self.character_url = character_url
        self.character_image_url = character_image_url
        self.name_eng = name_eng
        
    def to_dict(self):
        return {
            "character_url": self.character_url,
            "character_image_url": self.character_image_url,
            "name_eng": self.name_eng,
        }

class SideCharacter:
    def __init__(
            self,
            character_image_url: str,
            name_eng: str,  
            description_character: list,
            ) -> None:
        self.character_image_url = character_image_url
        self.name_eng = name_eng
        self.description_character = description_character

    
    def to_dict(self):
        return {
            "character_image_url": self.character_image_url,
            "name_eng": self.name_eng,
            "description_character": self.description_character,
        }

class Gadget:
    def __init__(
            self,
            gadget_url: str,
            name_eng: str,
            )-> None:
        self.gadget_url = gadget_url
        self.name_eng = name_eng
    
    def to_dict(self):
        return {
            "gadget_url": self.gadget_url,
            "name_eng": self.name_eng,
        }

class Case:
    def __init__(
            self,
            situation: str,
            case_image_url: str,
            crime_type: str,
            location: str,
            victims_name: str,
            cause_of_death: str,
            suspects_name_list: list,
            crime_description: str
            )-> None:
        
        self.situation = situation
        self.case_image_url = case_image_url
        self.crime_type = crime_type
        self.location = location
        self.victims_name = victims_name
        self.cause_of_death = cause_of_death
        self.suspects_name_list = suspects_name_list
        self.crime_description = crime_description


    def to_dict(self):
        return {
            "situation": self.situation,
            "case_image_url": self.case_image_url,
            "crime_type": self.crime_type,
            "location": self.location,
            "victims_name": self.victims_name,
            "suspects_name_list": self.suspects_name_list,
            "crime_description": self.crime_description,
        }

class Episode:
    def __init__(
            self,
            episode_number: str,
            international_episode_number: str,
            title_eng: str,
            title_kanji: str,
            title_romaji: str,
            description: str,
            season: str,
            airdate: str,
            main_characters: list,
            side_characters: list,
            case: Case,
            gadgets: list,
    ) -> None:
        
        self.episode_number = episode_number
        self.international_episode_number = international_episode_number
        self.title_eng = title_eng
        self.title_kanji = title_kanji
        self.title_romaji = title_romaji
        self.description = description
        self.season = season
        self.airdate = airdate
        self.main_characters = main_characters
        self.side_characters = side_characters
        self.cases = case.to_dict()
        self.gadgets = gadgets

    def to_dict(self):
        return {
            "episode_number": self.episode_number,
            "international_episode_number": self.international_episode_number,
            "title_eng": self.title_eng,
            "title_kanji": self.title_kanji,
            "title_romaji": self.title_romaji,
            "description": self.description,
            "season": self.season,
            "airdate": self.airdate,
            "main_characters": self.main_characters,
            "side_characters": self.side_characters,
            "cases": self.cases,
            "gadgets": self.gadgets,
        }
    
def read_file(file_path):
    with open(file_path, 'r', encoding="utf-8") as f:
        return f.read()


# pattern regx
info_table_pattern = re.compile(r'<table class="infobox"[^>]*>.*?</table>', re.DOTALL)

info_header_pattern = re.compile(r'<b>(.*?)</b>', re.DOTALL)

episode_pattern = re.compile(r'Episode\s+(\d+).*?Episode\s+(\d+)', re.DOTALL)

def extract_episode():

    episode_data = {
        "episode_number": "",
        "international_episode_number": "",
        "title_eng": "",
        "title_kanji": "",
        "title_romaji": "",
        "description": "",
        "season": "",
        "airdate": "",
        "main_characters": [],
        "side_characters": [],
        "cases": {}, 
        "gadgets": []
    }


    # for test
    html_content = read_file("episode.html")
    # print(html_content)

    info_table = re.findall(info_table_pattern, html_content)
    info_row_header_table = re.findall(info_header_pattern, info_table[0])

    print(info_row_header_table)

    episode_data["episode_number"], episode_data["international_episode_number"] = re.findall(episode_pattern ,info_row_header_table[0])[0]

    print(episode_data)

    


extract_episode()