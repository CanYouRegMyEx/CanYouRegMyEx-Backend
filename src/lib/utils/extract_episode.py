import re
from lib.utils.crawler import *
# from crawler import *
from pydantic import BaseModel
from typing import List

class MainCharacter(BaseModel):
    character_url: str
    character_image_url: str
    name_eng: str
    character_info: list[str]
    
class SideCharacter(BaseModel):
    character_image_url: str
    name_eng: str
    character_info: list
   
class Gadget(BaseModel):
    gadget_url: str
    name_eng: str

class CaseCard(BaseModel):
    case_image_url: str
    crime_type: str
    location: str
    victims_name: str
    cause_of_death: str
    suspects_name: str
    crime_description: str
    culprit: str

class BGMListing(BaseModel): 
    bgm_list: list[dict]

        
class Case(BaseModel):
    situation: list[str]    
    case_card_list: list[CaseCard]

class Resolution(BaseModel):
    Evidence: list[str]
    Conclusion: str
    Motive: str
    Aftermath: str
    Description: str
       
class Episode(BaseModel):
    episode_number: str
    international_episode_number: str
    episode_image_url: str
    title_eng: list[str]
    title_jpn: str
    description: str
    season: str
    airdate: list[str]   
    main_characters: list[MainCharacter]
    side_characters: list[SideCharacter]
    case: Case
    gadgets: list[Gadget]
    resolution: list[Resolution]
    bgm_list: list[dict]
   
def isContainNewline(text):
    return '\n' in text or text == ""
    
def read_file(file_path):
    with open(file_path, 'r', encoding="utf-8") as f:
        return f.read()

def get_data_between_tag(text: str):
    return re.findall(r'\s*[^>]+(?=<)', text)

def sub_tag(text: str):
    return re.sub(r'<[^>]+?>', "", text)

def sub_code_string(text: str):
    return re.sub(r'&#\d+', "", text) 


BASE_URL = "https://www.detectiveconanworld.com"

####################################### pattern regx #######################################

remove_tag_pattern = re.compile(r'<.*?>')

info_table_pattern = re.compile(r'<table class="infobox"[^>]*>.*?</table>', re.DOTALL)

info_header_pattern = re.compile(r'<b>(.*?)</b>', re.DOTALL)
info_row_key_vlaue_pattern = re.compile(r'<tr>\s*<th[^<]*>(?P<row_key>[^:]*):\s*..th>\s*<td>(?P<row_value>[^\n]+)', re.DOTALL)

episode_number_pattern = re.compile(r'Episode\s+(\d+).*?Episode\s+([^)]*)', re.DOTALL)
src_image_pattern = re.compile(r'src="([^"]+)"', re.DOTALL)

description_paragraph_pattern = re.compile(r'<p>\s*<i><b>.*\s</p>')
description_pattern = re.compile(r'\s*[^>&*;]+(?=<)')

main_characters_pattern = re.compile(r'<div\s+style="display:flex[^"]*".*?>\s(.*?)<h2>', re.DOTALL)
get_tag_a_pattern = re.compile(r'<a\s*href[^>]*>.*a>') 
href_name_src_character_pattern = re.compile(r'href="(?P<link_href>[^"]*)"\s*[^>]*><img\s*alt="(?P<name>[^"]*)"\ssrc="(?P<image_url>[^"]*)')

side_characters_pattern = re.compile(r'People<\/span></h\d>\s*<div\sstyle="overflow:hidden">\s*(.*?)<h3>', re.DOTALL)
get_tbody_pattern = re.compile(r'<tbody>\s*(.*?)\s*</tbody>', re.DOTALL)
get_tr_pattern = re.compile(r'<tr>\s*(.*?)</tr>', re.DOTALL)
get_li_pattern = re.compile(r'<li>([^<]*)', re.DOTALL)

crime_card_pattern = re.compile(r'<div\sclass="infobox-crime">\s*(?P<crime_type><div\s[^<]*</div>)\s*<div\sclass=[^<]*>\s*(?P<crime_image>.*)\s*<div\sclass="[^<]*(?P<crime_data>.*)')
crime_location_pattern = re.compile(r'Location:</strong></span> <span>([^<]*)')
crime_suspect_pattern = re.compile(r'Suspect:</strong></span>\s<span>([^<]*)')  
crime_attack_type = re.compile(r'Attack\sTypes:</strong></span>\s<span>([^<]*)')
crime_culpritc_pattern = re.compile(r'Culprit:</strong></span>\s<span>([^<]*)')
crime_description = re.compile(r'class="crime-description">([^<]*)')
crime_cause_of_death = re.compile(r'Cause of death:</strong></span>\s<span>([^<]*)')
crime_victim_pattern_normal = re.compile(r'Victim:</strong></span>\s<span>([^<]*)')
crime_victim_pattern_special = re.compile(r'Victim:</strong></span>\s<span><a\shref="[^"]*"\stitle="[^"]*">([^<]*)')

situation_pettern = re.compile(r'id="Situation">Situation</span></h3>\s*<p>([^<]*)</p>')

resolution_pattern = re.compile(r'id="Resolution[^"]*">(?:(?!overflow).)*overflow:\shidden;">\s*(?:(?!</div>).)*', re.DOTALL)
resolution_evidence_pattern = re.compile(r'Evidence</span></h\d>\s*(<ul>.*?</ul>)', re.DOTALL)
resolution_evidence_pattern_v2 = re.compile(r'Evidence<\/span><\/h\d>\s*.*?<\/ul>\s*(<ul>.*?<\/ul>)', re.DOTALL)
resolution_conclusion_pattern = re.compile(r'Conclusion</span></h\d>\s*(<p>.*?</p>)', re.DOTALL)
resolution_motive_pattern = re.compile(r'Motive<\/span><\/h\d>\s*(.*).')
resolution_aftermath_pattern = re.compile(r'Aftermath</span></h\d>\s*(<p>.*?</p>)',re.DOTALL)

between_tag_li_pattern = re.compile(r'<li>(.*?)<\/li>')
between_tag_p_pattern = re.compile(r'<p>(.*?)<\/p>', re.DOTALL)

bgm_table_pattern = re.compile(r'<div style="overflow:auto;">\s<table[^>]*>\s((?:(?!</table>).)*)' , re.DOTALL)
tr_section_pattern = re.compile(r'<tr>.*?<\/tr>', re.DOTALL)
row_data_td_pattern = re.compile(r'<td\sstyle="[^"]+">([^<]*)')
row_data_td_a_pattern = re.compile(r'<a\shref="([^"]*)[^>]*>([^<]*)')

main_characters_for_ep1_pattern = re.compile(r'Introduced<\/span></h\d>\s*<div\sstyle="overflow:hidden">\s*(.*?)<h3>', re.DOTALL)

br_split_pattern = re.compile(r' <br /> |<br /> | <br />|<br />') 

link_name_image_main_char_pattern = re.compile(r'<a\shref="(?P<link>[^"]+)"\stitle="(?P<name>[^"]+)"><img\salt="[^"]*"\ssrc="(?P<image_url>[^"]+)')

####################################### pattern regx #######################################

def extract_table_infobox(html_table, episode_data: dict)-> dict:
    info_row_header_table = re.findall(info_header_pattern, html_table[0])
    info_row_data_table = re.finditer(info_row_key_vlaue_pattern,html_table[0])

    episode_data["episode_number"], episode_data["international_episode_number"] = re.findall(episode_number_pattern ,info_row_header_table[0])[0]

    image = re.findall(src_image_pattern, html_table[0])
    if image == []:
        episode_data["episode_image_url"] = ""
    else:
        episode_data["episode_image_url"] = BASE_URL + re.findall(src_image_pattern, html_table[0])[0]

    for row in info_row_data_table:
        row_key = row.group('row_key')
        row_value = row.group('row_value')

        if row_key == "Title":
            list_title = []
            list_title.append(row_value)
            episode_data["title_eng"] = list_title
        
        elif row_key == "Japanese title":
            # row_vlaue = 図書館殺人事件 <br /> (Toshokan Satsujin Jiken)
            title = re.split(r' <br /> ', row_value)
            result_title = ''.join(title) 

            episode_data["title_jpn"] = sub_tag(result_title)

        elif row_key == "Original airdate":
            # ex. Original airdate:March 3, 1997 <br /> March 15, 2014 <b>(Remastered version)</b>
            original_airdate = re.split(r' <br />', row_value)
            airdate_list = []
            for airdate in original_airdate:
                airdate_list.append(sub_tag(airdate))
                
            episode_data["airdate"] = airdate_list

        elif row_key == "Broadcast rating":
            # ex. Broadcast rating:16.8%
            pass
        elif row_key == "Remastered rating":
            # ex. Remastered rating:8.8resolution_pattern%
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
            # list_title = re.split(br_split_pattern, row_value)
            # episode_data["title_eng"] = list_title

            pass
        elif row_key == "Dubbed episode":
            pass
        elif row_key == "English airdate":
        #    episode_data["airdate"] = re.split(br_split_pattern, row_value)  
            pass      

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
    description_p = re.sub(r'&#\d+?;', "'", description_p)

    description = ''
    for text in re.findall(description_pattern, description_p):
        if(len(text) > 3):
            description += text + ' '
    
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
                "name_eng":  char.group("name"),
                "character_info": []
            }

        character = MainCharacter(**main_character_data)
        main_character_list.append(character)

    episode_data["main_characters"] = main_character_list

    return episode_data

def extract_side_characters(div_side_characters, episode_data: dict)-> dict:

    side_characters_list = []

    for side_char in div_side_characters:

        for tbody in re.findall(get_tbody_pattern, side_char):

            if(tbody == []):
                return episode_data

            tr = re.findall(get_tr_pattern, tbody)
            header_table = tr[0]
            info_table = tr[1]

            character_data = {
                "character_image_url": "",
                "name_eng": get_data_between_tag(header_table)[0].split('\n')[0],
                "character_info": re.findall(get_li_pattern, info_table)
            }

            image = re.findall(src_image_pattern, info_table)

            if image == []:
                character_data["character_image_url"]= ""
            else :
                character_data["character_image_url"] = BASE_URL + image[0]
            

            character = SideCharacter(**character_data)
            side_characters_list.append(character)

        episode_data["side_characters"] = side_characters_list
    
    return episode_data

def extract_main_characters_for_ep1(div_main_characters, episode_data:dict)-> dict:
    
    main_characters_list = []

    # print(div_main_characters[0])
    tbody = re.findall(get_tbody_pattern,div_main_characters[0])

    if (tbody == []):
        return episode_data
    
    for tr in tbody:
        tr_data = re.findall(re.compile(r'<tr>.*?</tr>', re.DOTALL) , tr)[1]
        for data in re.finditer(link_name_image_main_char_pattern, tr_data):
            main_character_data = {
                "character_url": BASE_URL + data.group("link"),
                "character_image_url": BASE_URL + data.group("image_url"),
                "name_eng":  data.group("name"),
                "character_info": []
            }
        
        li = re.findall(re.compile(r'<ul>(.+)<\/ul>', re.DOTALL), tr_data)
        main_character_data["character_info"] = re.findall(r'>(.*?)<', li[0])

        character = MainCharacter(**main_character_data)
        main_characters_list.append(character)

    episode_data["main_characters"] = main_characters_list

    return episode_data

def extract_case(html_content, episode_data:dict )-> dict:

    case_data = {
        "situation": [],
        "case_card_list": []
    }
    
    case_data["situation"] = re.findall(situation_pettern, html_content)
    
    for crime in re.finditer(crime_card_pattern, html_content):
        crime_type = crime.group("crime_type")
        crime_image = crime.group("crime_image")
        crime_data = crime.group("crime_data")
        
        case_card_data = {
            "case_image_url": "",
            "crime_type": get_data_between_tag(crime_type)[0],
            "location": "",
            "victims_name": "",
            "cause_of_death": "",
            "suspects_name": "",
            "crime_description": "",
            "culprit": ""
        }

        image = re.findall(src_image_pattern, crime_image)

        if image == []:
            case_card_data["case_image_url"] = ""
        else:
            case_card_data["case_image_url"] = BASE_URL + image[0]
        
        case_card_data["location"] = location[0] if (location := re.findall(crime_location_pattern, crime_data)) else ""
        case_card_data["cause_of_death"] = cause_of_death[0] if (cause_of_death := re.findall(crime_cause_of_death, crime_data)) else ""
        case_card_data["crime_description"] = crime_des[0] if (crime_des := re.findall(crime_description, crime_data)) else ""
        case_card_data["culprit"] = culprit[0] if (culprit := re.findall(crime_culpritc_pattern, crime_data)) else ""
        case_card_data["suspects_name"] = suspect[0] if (suspect := re.findall(crime_suspect_pattern, crime_data)) else "" 

        victim = re.findall(crime_victim_pattern_normal, crime_data)
        if victim == [''] or victim == []:
            victim = re.findall(crime_victim_pattern_special, crime_data)
        
        if victim == []:
            victim = [""]

        case_card_data["victims_name"] = victim[0]


        case_card = CaseCard(**case_card_data)
        case_data["case_card_list"].append(case_card)
        
    episode_data["case"] = Case(**case_data)
   
    
    return episode_data

def extract_resolution(html_content, episode_data:dict) -> dict:
    resolution_list = []

    resolutions = re.findall(resolution_pattern, html_content)

    for resolution in resolutions:

        try:
           
            try:
                evidence = re.findall(resolution_evidence_pattern, resolution)[0]
            except:
                evidence = re.findall(resolution_evidence_pattern_v2, resolution)[0]

            evidence = evidence_list if (evidence_list:= re.findall(between_tag_li_pattern, evidence)) else []
            conclusion =  conclusion_text[0] if (conclusion_text:= re.findall(resolution_conclusion_pattern, resolution)) else ""
            motive = motive_text[0] if (motive_text:= re.findall(resolution_motive_pattern, resolution)) else ""
            aftermath = aftermath_text[0] if (aftermath_text:= re.findall(resolution_aftermath_pattern, resolution)) else "" 

            
            if evidence == [] and conclusion == "" and motive == "" and aftermath == "":
                raise Exception("resolution data not found")

            conclusion_p = re.findall(between_tag_p_pattern, conclusion)[0]
            conclusion_p = sub_tag(conclusion_p)

            resolution_data = {
                "Evidence": evidence,
                "Conclusion": conclusion_p,
                "Motive" : sub_tag(motive),
                "Aftermath": sub_tag(aftermath),
                "Description": ""
            }

            resolution_object  = Resolution(**resolution_data)
            resolution_list.append(resolution_object)

        except:            
            resolution_data = {
                "Evidence": [],
                "Conclusion": "",
                "Motive" : "",
                "Aftermath": "",
                "Description": re.findall(r'Show spoilers\s[^;]*;(.*)', sub_tag(resolution))[0]
            }

            print(resolution_data)
            resolution_object  = Resolution(**resolution_data)
            resolution_list.append(resolution_object)

    episode_data["resolution"] = resolution_list

    return episode_data


def extract_bgm(table, episode_data: dict)-> dict:

    if table == []:
        episode_data["bgm_list"] = []
        return episode_data

    bgm_list = []

    if table == []:
        return episode_data

    tr_list = re.findall(tr_section_pattern, table[0])
    for tr in tr_list[1::]:
        row_data_tr = re.findall(row_data_td_pattern, tr)
        row_data_tr_a = re.findall(row_data_td_a_pattern, tr)

        if row_data_tr_a == []:
            continue

        OST_url , OST_name = row_data_tr_a[0]

        bgm_dict = {
            "Song Title": row_data_tr[1],
            "Romaji" : row_data_tr[2],
            "Translation": row_data_tr[3],
            "OST_name": OST_name,
            "OST_url": BASE_URL + OST_url
        }

        bgm_list.append(bgm_dict)

    episode_data["bgm_list"] = bgm_list

    return episode_data

def main_extract_episode(url: str):

    episode_data = {
        "episode_number": "",
        "international_episode_number": "",
        "episode_image_url": "",
        "title_jpn": "",
        "title_eng": list[str],
        "description": "",
        "season": "",
        "airdate": list[str],
        "main_characters": list[MainCharacter],
        "side_characters": list[SideCharacter],
        "case": None, 
        "gadgets": [],
        "resolution" : list[Resolution],
        "bgm_list" : list[dict]
    }


    # html_content = crawl(url)
    html_content = crawl(url)

    info_table = re.findall(info_table_pattern, html_content)
    episode_data = extract_table_infobox(info_table, episode_data)
 
    paragraph_description = re.findall(description_paragraph_pattern, html_content)
    episode_data = extract_episode_description(paragraph_description, episode_data )

    try:
        div_main_characters = re.findall(main_characters_pattern, html_content)
        episode_data = extract_main_characters(div_main_characters, episode_data)

    except:
        div_main_characters = re.findall(main_characters_for_ep1_pattern, html_content)
        episode_data = extract_main_characters_for_ep1(div_main_characters, episode_data)
    
    div_side_characters = re.findall(side_characters_pattern, html_content)
    episode_data = extract_side_characters(div_side_characters, episode_data)

    # Case 
    episode_data = extract_case(html_content, episode_data)
    
    #Resolution
    episode_data = extract_resolution(html_content, episode_data)

    table_bgm_listing = re.findall(bgm_table_pattern, html_content)
    episode_data = extract_bgm(table_bgm_listing, episode_data)

    episode = Episode(**episode_data)
    
    return episode

    


# main_extract_episode("https://www.detectiveconanworld.com/wiki/Kid_vs._Amuro:_Queen%27s_Bang")