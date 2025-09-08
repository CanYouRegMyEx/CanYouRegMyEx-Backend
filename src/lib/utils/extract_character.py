import re
from typing import List, Dict
from lib.utils.crawler import *
from lib.utils.filter_pipeline import *
from pydantic import BaseModel

class Profile(BaseModel):
    name_eng: str
    names_eng_localised: List[str]
    name_jpn: str
    ages: List[str]
    gender: str
    heights: List[str]
    weights: List[str]
    birthday: str
    occupations: List[str]
    statuses: List[str]
    actors: Dict[str, List[str]]
    profile_picture_url: str
    
class Character(BaseModel):
    profile: Profile
    summary: List[str]
    background: Dict[str, List[str]]
    appearance: Dict[str, List[str]]
    personality: Dict[str, List[str]]
    skills: Dict[str, List[str]]
    image_urls: List[str]
    
# Match Patterns - Common
general_data_extraction_pattern = re.compile(r'([^>\n]+)(?=<|\n|$)', re.DOTALL)

# Match Patterns - Profiles
profile_table_pattern = re.compile(r'<table class="infobox"[^>]*>.*?</table>', re.DOTALL)
h1_character_name_pattern = re.compile(r'<h1 id="firstHeading" class="firstHeading"[^>]*?>(.+?)<\/h1>')
profile_table_rows_pattern = re.compile(r'<th[^>]*?>(?P<row_header>.+):\n<\/th>\n<td>(?P<row_data>.+)\n<\/td>')
profile_row_data_extraction_pattern = re.compile(r'^([^><]+?)<|>([^><]+?)<|>([^><]+?)$')

# Match Patterns - Paragraphs
container_div_pattern = re.compile(r'<div class="mw-parser-output">(.+)<\/div>\n<!--', re.DOTALL)
summary_pattern = re.compile(r'<\/tbody><\/table>\n(?:<p>.+\n<\/p>)*')
h2_paragraph_pattern = re.compile(r'(?:<span class="mw-headline"[^>]+>(?P<h2_paragraphs_header>.+?)<\/span><\/h2>\n*).+?<h2>', re.DOTALL)
generic_paragraph_pattern = re.compile(r'<\/h2>.+?<h3>', re.DOTALL)
h3_paragraph_pattern = re.compile(r'(?:<span class="mw-headline"[^>]+>(?P<h3_paragraphs_header>.+?)<\/span><\/h3>\n*).+?(?:<h3>|<h2>)', re.DOTALL)
first_h3_header_cleansing_pattern = re.compile(r'<h3><span class="mw-headline"[^>]*>(.+)')
paragraph_text_extraction_pattern = re.compile(r'<p>(.+\s+)<\/p>')
image_extraction_pattern = re.compile(r'<img.+src="(?P<url>\/wiki\/images\/thumb.+?)".+width="(?P<width>[^"]+?)" height="(?P<height>[^"]+?)"')

# Split Patterns
br_split_pattern = re.compile(r' <br /> |<br /> | <br />|<br />')

# Substitute Patterns
reference_substitute_pattern = re.compile(r'&#\d+;\d+&#\d+;|&#\d+;')
language_help_substitute_pattern = re.compile(r'<span[^>]*>\?<\/span>')
url_substitute_pattern = re.compile(r'(<a.+?>)|(<\/a>)')
i_tag_substitute_pattern = re.compile(r'<i>|<\/i>')
sup_tag_substitute_pattern = re.compile(r'<sup.+?>|<\/sup>')
span_tag_substitute_pattern = re.compile(r'<span[^>]*?>|<\/span>')
ruby_tag_substitute_pattern = re.compile(r'<ruby>|<\/ruby>')
rp_tag_substitute_pattern = re.compile(r'<rp>.+<\/rp>')

tag_cleanse_filter_pipeline = FilterPipeline([
    i_tag_substitute_pattern,
    sup_tag_substitute_pattern,
    reference_substitute_pattern,
    language_help_substitute_pattern,
    url_substitute_pattern,
], "-----")

furigana_cleanse_filter_pipeline = FilterPipeline([
    ruby_tag_substitute_pattern,
    rp_tag_substitute_pattern
], "--")

def extract_image_urls(html_string):
    image_urls = []
    for match in re.finditer(image_extraction_pattern, html_string):
        url = match.group("url")
        width = int(match.group("width"))
        height = int(match.group("height"))
        if width <= 60 and height <= 60: continue
        
        image_urls.append("https://www.detectiveconanworld.com"+url)
    
    return image_urls

def extract_paragraph_texts(paragraphs_html_str):
    paragraphs = []
    paragraph_texts = re.findall(paragraph_text_extraction_pattern, paragraphs_html_str)
    for p_text in paragraph_texts:
        if p_text:
            paragraph_chunks = re.findall(general_data_extraction_pattern, p_text)
            paragraph = "".join(paragraph_chunks)
            paragraphs.append(paragraph)
    return paragraphs

def extract_character_profile_picture(html_string):
    image_urls = extract_image_urls(html_string)
    return extract_image_urls(html_string)[0] if image_urls else ""

def extract_character_profile(html_string):

    profile_data = {
        "name_eng": "",
        "names_eng_localised": [],
        "name_jpn": "",
        "ages": [],
        "gender": "",
        "heights": [],
        "weights": [],
        "birthday": "",
        "occupations": [],
        "statuses": [],
        "actors": {
            "voices_jpn": [],
            "voices_eng": [],
            "drama_actors": []
        },
        "profile_picture_url": ""
    }

    profile_table = re.findall(profile_table_pattern, html_string)[0]
    profile_table_cleansed = tag_cleanse_filter_pipeline.filter(profile_table)
    
    profile_data["name_eng"] = re.findall(h1_character_name_pattern, html_string)[0]
    profile_data["profile_picture_url"] = extract_character_profile_picture(html_string)

    for match in re.finditer(profile_table_rows_pattern, profile_table_cleansed):
        row_header = match.group("row_header")
        row_data = match.group("row_data")

        if row_header == "Japanese name":
            row_data_cleansed = furigana_cleanse_filter_pipeline.filter(row_data)
            name_jpn, romanji = re.split(br_split_pattern, row_data_cleansed)
            name_jpn = re.sub(span_tag_substitute_pattern, '', name_jpn)
            profile_data["name_jpn"] = name_jpn

        elif row_header == "English name":
            names_eng = re.split(br_split_pattern, row_data)
            profile_data["names_eng_localised"] = names_eng

        elif row_header == "Age":
            ages = re.split(br_split_pattern, row_data)
            profile_data["ages"] = ages
        
        elif row_header == "Gender":
            profile_data["gender"] = row_data
        
        elif row_header == "Height":
            heights = re.findall(profile_row_data_extraction_pattern, row_data)
            heights = [h for sub_list in heights for h in sub_list if h != ""]
            profile_data["heights"] = heights if heights else [row_data]

        elif row_header == "Weight":
            weights = re.findall(profile_row_data_extraction_pattern, row_data)
            weights = [w for sub_list in weights for w in sub_list if w != ""]
            profile_data["weights"] = weights if weights else [row_data]

        elif row_header == "Date of birth":
            profile_data["birthday"] = row_data

        elif row_header == "Occupation":
            occupations = re.split(br_split_pattern, row_data)
            occupations = [o.strip() for o in occupations]
            profile_data["occupations"] = occupations

        elif row_header == "Status":
            statuses = re.split(br_split_pattern, row_data)
            profile_data["statuses"] = statuses

        elif row_header == "Japanese voice":
            voices_jpn = re.split(br_split_pattern, row_data)
            profile_data["actors"]["voices_jpn"] = voices_jpn

        elif row_header == "English voice":
            voices_eng = re.split(br_split_pattern, row_data)
            profile_data["actors"]["voices_eng"] = voices_eng
        
        elif row_header == "Drama actor":
            drama_actors = re.split(br_split_pattern, row_data)
            profile_data["actors"]["drama_actors"] = drama_actors

    profile = Profile(**profile_data)
    return profile
    
def extract_character_paragraphs(html_string):
    container_div = re.findall(container_div_pattern, html_string)[0]
    container_div_cleansed = tag_cleanse_filter_pipeline.filter(container_div)
    
    paragraphs_data = {
        "summary": [],
        "background": {
            "generic": [],
        },
        "appearance": {
            "generic": [],
        },
        "personality": {
            "generic": [],
        },
        "skills": {
            "generic": [],
        }
    }

    summary_html = re.findall(summary_pattern, container_div_cleansed)[0]
    summary_paragraphs = extract_paragraph_texts(summary_html)
    paragraphs_data["summary"] = summary_paragraphs

    for h2_match in re.finditer(h2_paragraph_pattern, container_div_cleansed):
        h2_paragraphs_header = h2_match.group("h2_paragraphs_header").lower()
        if h2_paragraphs_header == "abilities": h2_paragraphs_header = "skills"
        h2_paragraphs_html = h2_match[0]
        
        if h2_paragraphs_header in paragraphs_data:

            h3_exists = len(re.findall(h3_paragraph_pattern, h2_paragraphs_html)) > 0
            
            if h3_exists:
                generic_paragraphs_raw = re.findall(generic_paragraph_pattern, h2_paragraphs_html)[0]
                generic_paragraphs = extract_paragraph_texts(generic_paragraphs_raw)
                paragraphs_data[h2_paragraphs_header]["generic"] = generic_paragraphs

                for i, h3_match in enumerate(re.finditer(h3_paragraph_pattern, h2_paragraphs_html)):
                    h3_paragraphs_header = h3_match.group("h3_paragraphs_header")
                    if i == 0: h3_paragraphs_header = "".join(re.findall(first_h3_header_cleansing_pattern, h3_paragraphs_header))
                    h3_paragraphs_header = re.sub(url_substitute_pattern, '', h3_paragraphs_header)
                    
                    h3_paragraphs_html = h3_match[0]
                    h3_paragraphs = extract_paragraph_texts(h3_paragraphs_html)
                    paragraphs_data[h2_paragraphs_header][h3_paragraphs_header] = h3_paragraphs
            
            else:
                
                h2_paragraphs = extract_paragraph_texts(h2_paragraphs_html)
                paragraphs_data[h2_paragraphs_header]["generic"] = h2_paragraphs
    
    return paragraphs_data

def extract_character(url):
    html_string = crawl(url)

    profile = extract_character_profile(html_string)
    paragraphs_dict = extract_character_paragraphs(html_string)
    image_urls = extract_image_urls(html_string)
    character = Character(profile=profile, **paragraphs_dict, image_urls=image_urls[1:10])

    return character
    