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
            episode_image_url: str,
            title_eng: str,
            title_jpn: str,
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
        self.episode_image_url = episode_image_url
        self.title_eng = title_eng
        self.title_jpn = title_jpn
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
            "episode_image_url": self.episode_image_url,
            "title_jpn": self.title_jpn,
            "title_eng": self.title_eng,
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

def get_data_between_tag(str: str):
    return re.findall(r'\s*[^>]+(?=<)', str)

BASE_URL = "https://www.detectiveconanworld.com"

####################################### pattern regx #######################################

info_table_pattern = re.compile(r'<table class="infobox"[^>]*>.*?</table>', re.DOTALL)

info_header_pattern = re.compile(r'<b>(.*?)</b>', re.DOTALL)
info_row_key_vlaue_pattern = re.compile(r'<tr>\s*<th>(?P<row_key>[^:]*):\s*..th>\s*<td>(?P<row_value>[^\n]+)', re.DOTALL)

episode_number_pattern = re.compile(r'Episode\s+(\d+).*?Episode\s+(\d+)', re.DOTALL)
episode_image_pattern = re.compile(r'src="([^"]+)"', re.DOTALL)

description_paragraph_pattern = re.compile(r'<p>\s*<i><b>.*\s</p>')
description_pattern = re.compile(r'\s*[^>&*;]+(?=<)')

####################################### pattern regx #######################################

def extract_table_infobox(html_table, episode_data: dict):
    info_row_header_table = re.findall(info_header_pattern, html_table[0])
    info_row_data_table = re.finditer(info_row_key_vlaue_pattern,html_table[0])

    episode_data["episode_number"], episode_data["international_episode_number"] = re.findall(episode_number_pattern ,info_row_header_table[0])[0]
    episode_data["episode_image_url"] = BASE_URL + re.findall(episode_image_pattern, html_table[0])[0]

    for row in info_row_data_table:
        row_key = row.group('row_key')
        row_value = row.group('row_value')

        if row_key == "Japanese title":
            # row_vlaue = 図書館殺人事件 <br /> (Toshokan Satsujin Jiken)
            title = re.split(r' <br /> ', row_value)
            episode_data["title_jpn"] = ''.join(title) 

        elif row_key == "Original airdate":
            # ex. Original airdate:March 3, 1997 <br /> March 15, 2014 <b>(Remastered version)</b>
            original_airdate = re.split(r' <br />', row_value)[0]

        elif row_key == "Broadcast rating":
            # ex. Broadcast rating:16.8%
            pass
        elif row_key == "Remastered rating":
            # ex. Remastered rating:8.8%
            pass
        elif row_key == "Manga case":
            # ex. Manga case:#26
            pass
        elif row_key == "Season":
            # Season:<a href="/wiki/Season_2" title="Season 2">2</a>
            episode_data["season"] = get_data_between_tag(row_value)[0]
            pass
        elif row_key == "Manga source":
            # ex. Manga source:<a href="/wiki/Volume_10#Library_Murder_Case" title="Volume 10">Volume 10: Files 6-8 (096-098)</a>
            pass
        elif row_key == "English title":
            # ex. English title:The Book Without Pages
            episode_data["title_eng"] = row_value
            pass
        elif row_key == "Dubbed episode":
            pass
        elif row_key == "English airdate":
           episode_data["airdate"] = row_value           

        # elif row_key == "Cast":
        #     pass
        # elif row_key == "Case solved by":
        #     pass
        # elif row_key == "Next Conan's Hint":
        #     pass
        # elif row_key == "Director":
        #     pass
        # elif row_key == "Organizer":
        #     pass
        # elif row_key == "Storyboard":
        #     pass
        # elif row_key == "Episode director":
        #     pass
        # elif row_key == "Animation director":
        #     pass
        # elif row_key == "Character design":
        #     pass

    return episode_data
    
def extract_episode_description(html_content, episode_data):
    description_p = html_content[0]
    description = ''
    for text in re.findall(description_pattern, description_p):
        if(len(text) > 3):
            description += text+' '
    episode_data["description"] = description

    return episode_data
    

def main_extract_episode():

    episode_data = {
        "episode_number": "",
        "international_episode_number": "",
        "episode_image_url": "",
        "title_jpn": "",
        "title_eng": "",
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
    episode_data = extract_table_infobox(info_table, episode_data)
 
    paragraph_description = re.findall(description_paragraph_pattern, html_content)
    episode_data = extract_episode_description(paragraph_description, episode_data )

    
    
    print(episode_data)

    

    


main_extract_episode()