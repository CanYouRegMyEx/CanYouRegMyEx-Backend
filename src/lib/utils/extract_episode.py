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
            character_info: list,
            ) -> None:
        self.character_image_url = character_image_url
        self.name_eng = name_eng
        self.character_info = character_info

    
    def to_dict(self):
        return {
            "character_image_url": self.character_image_url,
            "name_eng": self.name_eng,
            "character_info": self.character_info,
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

class CaseCard:
    def __init__(
            self,
            case_image_url: str,
            crime_type: str,
            location: str,
            victims_name: str,
            cause_of_death: str,
            suspects_name_list: list,
            crime_description: str,
            culprit: str
            ) -> None:
        
        self.case_image_url = case_image_url
        self.crime_type = crime_type
        self.location = location
        self.victims_name = victims_name
        self.cause_of_death = cause_of_death
        self.suspects_name_list = suspects_name_list
        self.crime_description = crime_description
        self.culprit = culprit

    def to_dict(self):
        return {
            "case_image_url": self.case_image_url,
            "crime_type": self.crime_type,
            "location": self.location,
            "victims_name": self.victims_name,
            "cause_of_death": self.cause_of_death,
            "suspects_name_list": self.suspects_name_list,
            "crime_description": self.crime_description,
            "culprit": self.culprit,
        }

        
class Case:
    def __init__(
            self,
            situation: str,
            case_card_list: list[CaseCard]

            )-> None:
        
        self.situation = situation
        self.case_card_list =  case_card_list

    def to_dict(self):
        return {
            "situation": self.situation,
            "case_card_list": [card.to_dict() for card in self.case_card_list],
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
            main_characters: list[MainCharacter],
            side_characters: list[SideCharacter],
            case: list[Case],
            gadgets: list[Gadget],
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
src_image_pattern = re.compile(r'src="([^"]+)"', re.DOTALL)

description_paragraph_pattern = re.compile(r'<p>\s*<i><b>.*\s</p>')
description_pattern = re.compile(r'\s*[^>&*;]+(?=<)')

main_characters_pattern = re.compile(r'<div\s+style="display:flex[^"]*".*?>\s(.*?)<h2>', re.DOTALL)
get_tag_a_pattern = re.compile(r'<a\s*href[^>]*>.*a>') 
href_name_src_character_pattern = re.compile(r'href="(?P<link_href>[^"]*)"\s*[^>]*><img\s*alt="(?P<name>[^"]*)"\ssrc="(?P<image_url>[^"]*)')

side_characters_pattern = re.compile(r'<div\sstyle="overflow:hidden">\s*(.*?)<h3>', re.DOTALL)
get_tbody_pattern = re.compile(r'<tbody>\s*(.*?)\s*</tbody>', re.DOTALL)
get_tr_pattern = re.compile(r'<tr>\s*(.*?)</tr>', re.DOTALL)
get_li_pattern = re.compile(r'<li>([^<]*)', re.DOTALL)

crime_card_pattern = re.compile(r'<div\sclass="infobox-crime">\s*(?P<crime_type><div\s[^<]*</div>)\s*<div\sclass=[^<]*>\s*(?P<crime_image>.*)\s*<div\sclass="[^<]*(?P<crime_data>.*)')
crime_location_pattern = re.compile(r'Location:</strong></span> <span>([^<]*)')
crime_suspect_pattern = re.compile(r'Suspect:</strong></span>\s<span>([^<]*)')  #list
crime_attack_type = re.compile(r'Attack\sTypes:</strong></span>\s<span>([^<]*)')
crime_culpritc_pattern = re.compile(r'Culprit:</strong></span>\s<span>([^<]*)')
crime_description = re.compile(r'class="crime-description">([^<]*)')
crime_cause_of_death = re.compile(r'Cause of death:</strong></span>\s<span>([^<]*)')
crime_victim_pattern_normal = re.compile(r'Victim:</strong></span>\s<span>([^<]*)')
crime_victim_pattern_shit = re.compile(r'Victim:</strong></span>\s<span><a\shref="[^"]*"\stitle="[^"]*">([^<]*)')


####################################### pattern regx #######################################

def extract_table_infobox(html_table, episode_data: dict)-> dict:
    info_row_header_table = re.findall(info_header_pattern, html_table[0])
    info_row_data_table = re.finditer(info_row_key_vlaue_pattern,html_table[0])

    episode_data["episode_number"], episode_data["international_episode_number"] = re.findall(episode_number_pattern ,info_row_header_table[0])[0]
    episode_data["episode_image_url"] = BASE_URL + re.findall(src_image_pattern, html_table[0])[0]

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
    
def extract_episode_description(description_p, episode_data: dict)-> dict:
    description_p = description_p[0]
    description = ''
    for text in re.findall(description_pattern, description_p):
        if(len(text) > 3):
            description += text+' '
    episode_data["description"] = description

    return episode_data
    
def extract_main_characters(div_main_characters, episode_data: dict)-> dict: 
    div_main_characters = div_main_characters[0]
    
    main_character_list:list[MainCharacter] = []

    for tag_a_character in re.findall(get_tag_a_pattern, div_main_characters):
        # print(tag_a_character, "\n")   
        if(tag_a_character == []):
            return episode_data

        for char in re.finditer(href_name_src_character_pattern, tag_a_character):
            main_character_data = {
                "character_url": BASE_URL + char.group("link_href"),
                "character_image_url": BASE_URL + char.group("image_url"),
                "name_eng":  char.group("name")
            }

        character = MainCharacter(**main_character_data)
        main_character_list.append(character)

    episode_data["main_characters"] = main_character_list

    return episode_data

def extract_side_characters(div_side_characters, episode_data: dict)-> dict:

    side_characters_list = []

    for tbody in re.findall(get_tbody_pattern, div_side_characters[0]):

        if(tbody == []):
            return episode_data

        tr = re.findall(get_tr_pattern, tbody)
        header_table = tr[0]
        info_table = tr[1]

        character_data = {
            "character_image_url": BASE_URL + re.findall(src_image_pattern, info_table)[0],
            "name_eng": get_data_between_tag(header_table)[0].split('\n')[0],
            "character_info": re.findall(get_li_pattern, info_table)
        }

        character = SideCharacter(**character_data)
        side_characters_list.append(character)

    episode_data["side_characters"] = side_characters_list
    
    return episode_data

def extract_case(html_content, episode_data:dict )-> dict:

    crime_data = {
        "situation": "",
        "case_card_list": list[CaseCard]
    }
    

    for crime in re.finditer(crime_card_pattern, html_content):
        crime_type = crime.group("crime_type")
        crime_image = crime.group("crime_image")
        crime_data = crime.group("crime_data")
        
        case_card_data = {
            "case_image_url": BASE_URL + re.findall(src_image_pattern, crime_image)[0] ,
            "crime_type": get_data_between_tag(crime_type)[0],
            "location": re.findall(crime_location_pattern, crime_data)[0],
            "victims_name": "",
            "cause_of_death": re.findall(crime_cause_of_death, crime_data)[0],
            "suspects_name_list": list[str],
            "crime_description": re.findall(crime_description, crime_data)[0],
            "culprit": re.findall(crime_culpritc_pattern, crime_data)[0]
        }
        

        print(crime_data, "\n")
    
        # print(case_data, "\n")

        

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
        "main_characters": list[MainCharacter],
        "side_characters": list[SideCharacter],
        "cases": Case, 
        "gadgets": list[Gadget]
    }


    # for test
    html_content = read_file("episode.html")
    # print(html_content)

    info_table = re.findall(info_table_pattern, html_content)
    episode_data = extract_table_infobox(info_table, episode_data)
 
    paragraph_description = re.findall(description_paragraph_pattern, html_content)
    episode_data = extract_episode_description(paragraph_description, episode_data )

    div_main_characters = re.findall(main_characters_pattern, html_content)
    episode_data = extract_main_characters(div_main_characters, episode_data)
    
    div_side_characters = re.findall(side_characters_pattern, html_content)
    episode_data = extract_side_characters(div_side_characters, episode_data)

    # Case 
    episode_data = extract_case(html_content, episode_data)
    
    # print(episode_data)

    

    


main_extract_episode()