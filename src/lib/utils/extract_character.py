import re
from typing import List, Dict

class Profile:
    def __init__(
            self, 
            name_eng: str, 
            surname_eng: str, 
            name_jpn: str, 
            surname_jpn: str, 
            ages: List[str],
            gender: str, 
            height: str, 
            weight: str, 
            birthday: str,
            occupations: str,
            status: List[str], 
            actors: Dict[str, List[str]],
            profile_picture_url: str
        ):

        self.name_eng = name_eng
        self.surname_eng = surname_eng
        self.name_jpn = name_jpn
        self.surname_jpn = surname_jpn
        self.ages = ages
        self.gender = gender
        self.height = height
        self.weight = weight
        self.birthday = birthday
        self.occupations = occupations
        self.status = status
        self.actors = actors
        self.profile_picture_url = profile_picture_url
    
    def to_dict(self):
        return {
            "name_eng": self.name_eng,
            "surname_eng": self.surname_eng,
            "name_jpn": self.name_jpn,
            "surname_jpn": self.surname_jpn,
            "ages": self.ages,
            "gender": self.gender,
            "height": self.height,
            "weight": self.weight,
            "birthday": self.birthday,
            "occupations": self.occupations,
            "status": self.status,
            "actors": self.actors,
            "profile_picture_url": self.profile_picture_url,
        }
    
class Character:
    def __init__(
            self,
            profile: Profile,
            summary: str,
            background: str,
            appearance: str,
            personality: str,
            image_urls: List[str]
        ):
        
        self.profile = profile
        self.summary = summary
        self.background = background
        self.appearance = appearance
        self.personality = personality
        self.image_urls = image_urls

    def to_dict(self):
        return {
            "profile": self.profile.to_dict(),
            "summary": self.summary,
            "background": self.background,
            "appearance": self.appearance,
            "personality": self.personality,
            "image_urls": self.image_urls
        }

# Match Patterns
profile_table_pattern = re.compile(r'<table class="infobox"[^>]*>.*?</table>', re.DOTALL)
profile_table_rows_pattern = re.compile(r'<th[^>]*>(?P<row_header>[^<]+):\s*</th>\s*<td>(?:<^\n+>)?(?P<row_data>[^\n]+)\n</td>', re.DOTALL)
general_data_extraction_pattern = re.compile(r'([^>\n]+)(?=<|\n)', re.DOTALL)
status_extraction_pattern = re.compile(r'\s*([^>\n]+)(?=<|$)', re.DOTALL)
actors_pattern = re.compile(r'\s*([^>\n]+)(?=<|\n|$)', re.DOTALL)
container_div_pattern = re.compile(r'<div class="mw-parser-output">(.+)<\/div>\n<!--', re.DOTALL)
summary_pattern = re.compile(r'<\/tbody><\/table>\n(?:<p>.+\n<\/p>)*')
paragraph_with_header_pattern = re.compile(r'(?:<h2><span[^>]+>(?P<p_header>.+?)<\/span><\/h2>\n*)(?:(?:(?:<div class="thumb .+)*)*\n*(?:(?:<p>.+\s*<\/p>)*\n?))*')
paragraph_html_extraction_pattern = re.compile(r'<p>(.+\s+)<\/p>')
image_extraction_pattern = re.compile(r'<img.+src="(?P<url>.+?)"')

# Split Patterns
br_split_pattern = re.compile(r' <br /> |<br /> | <br />')
nakaten_split_pattern = re.compile(r'・')
space_split_pattern = re.compile(r' ')

# Substitute Patterns
reference_substitute_pattern = re.compile(r'&#\d+;\d+&#\d+;|&#\d+;')
language_help_substitute_pattern = re.compile(r'<span[^>]*>\?<\/span>')

def read_file(file_path):
    with open(file_path, 'r', encoding="utf-8") as f:
        return f.read()

def extract_image_urls(html_string):
    image_urls = re.findall(image_extraction_pattern, html_string)
    image_urls = ["https://www.detectiveconanworld.com"+url for url in image_urls]
    return image_urls[:10]

def extract_character_profile_picture(html_string):
    return extract_image_urls(html_string)[0]

def extract_character_profile(html_string):  
    profile_table = re.findall(profile_table_pattern, html_string)
    table_html = profile_table[0]

    profile_data = {
        "name_eng": "", "surname_eng": "",
        "name_jpn": "", "surname_jpn": "",
        "ages": [],
        "gender": "",
        "height": [],
        "weight": [],
        "birthday": "",
        "occupations": [],
        "status": "",
        "actors": {
            "voices_jpn": [],
            "voices_eng": [],
            "drama_actors": []
        },
        "profile_picture_url": ""
    }

    profile_data["profile_picture_url"] = extract_character_profile_picture(html_string)

    for row in re.finditer(profile_table_rows_pattern, table_html):

        row_header = row.group('row_header')
        row_data = row.group('row_data')
        row_data_cleansed = re.sub(reference_substitute_pattern, '', row_data)

        if row_header == "Japanese name":
            
            # 1.) Names like "工藤 新一"; Separated by a whitespace.
            # 2.) Names like "ジェイムズ・ブラック"; Separated by a nakaten (・)
            # * Type 1 is native Japanese and name/surname must be reversed.
            # * Both have a romanji version after, separated by a " <br /> ", such as "(Jeimuzu Burakku)".
            # EX: ジェイムズ・ブラック <br /> (Jeimuzu Burakku)

            full_name_jpn, romanji = re.split(br_split_pattern, row_data_cleansed)
            names_splitted_by_space = re.split(space_split_pattern, full_name_jpn)
            names_splitted_by_nakaten = re.split(nakaten_split_pattern, full_name_jpn)

            if len(names_splitted_by_space) > 1:
                profile_data["surname_jpn"], profile_data["name_jpn"] = names_splitted_by_space
            elif len(names_splitted_by_nakaten) > 1:
                profile_data["name_jpn"], profile_data["surname_jpn"] = names_splitted_by_nakaten
                
        elif row_header == "English name":

            name_eng, surname_eng = re.split(space_split_pattern, row_data_cleansed)
            profile_data["name_eng"] = name_eng
            profile_data["surname_eng"] = surname_eng
        
        elif row_header == "Age":

            ages = re.findall(general_data_extraction_pattern, row_data_cleansed)
            profile_data["ages"] = ages

        elif row_header == "Gender":

            profile_data["gender"] = row_data_cleansed

        elif row_header == "Height":

            # Height's row_data includes an encoded [ and ] for the superscripted info reference
            # and occasionally contains a demented amount of inline-css.
            # Also contains both metric and imperial units,
            # the latter of which may display an escape backslash in front of either ' or ", just ignore them.
            # EX: "5'8.5\""

            height = re.findall(general_data_extraction_pattern, row_data_cleansed)
            profile_data["height"] = height
            # print(height[1])     # This will be left here to show that the imperial unit is printed properly.

        elif row_header == "Weight":

            # Height's row_data_cleansed includes an encoded [ and ] for the superscripted info reference
            # and occasionally contains a demented amount of inline-css.
            # Also contains both metric and imperial units.

            weight = re.findall(general_data_extraction_pattern, row_data_cleansed)
            profile_data["weight"] = weight

        elif row_header == "Date of birth":

            # If some characters have multiple birthdates I will go back to my home in rural Isan and start farming.

            birthday = re.findall(general_data_extraction_pattern, row_data_cleansed)[0]
            profile_data["birthday"] = birthday

        elif row_header == "Occupation":

            # If multiple, are splitted by " <br /> "
            # EX: Teitan High School student <br /> Karate club captain <br /> Kanto Region karate champion
            # If singular, my regex breaks and I'll be real with you, I'm not doing that again.

            occupations = re.findall(general_data_extraction_pattern, row_data_cleansed)
            if not occupations and row_data_cleansed: occupations.append(row_data_cleansed)
            occupations = [occ.strip() for occ in occupations if occ != " "]
            profile_data["occupations"] = occupations

        elif row_header == "Status":

            # If multiple, are splitted by " <br /> "
            # Some may also have additional notes attached.
            # EX: Alive, Dead (for the Black Organization)
            # So basically, I split each entry using br first, then put the unassembled ones together afterwards.

            statuses = re.split(br_split_pattern, row_data_cleansed)
            for i in range(1, len(statuses)):
                partial_sentences = re.findall(status_extraction_pattern, statuses[i])
                statuses[i] = "".join(partial_sentences)

            profile_data["status"] = statuses

        elif row_header == "Japanese voice":

            # If multiple, are splitted by " <br /> "
            # The actors' names are hyperlinked, some also comes with additional, non-hyperlink notes.
            # The names will be splitted first, then will be filtered out of the link in the for loop.
            # Each name and their corresponding description are then joined.

            voices_jpn = re.split(br_split_pattern, row_data_cleansed)

            for i in range(len(voices_jpn)):
                voices_jpn[i] = re.findall(actors_pattern, voices_jpn[i])
                voices_jpn[i] = " ".join(voices_jpn[i])

            profile_data["actors"]["voices_jpn"].append(voices_jpn)

        elif row_header == "English voice":

            voices_eng = re.split(br_split_pattern, row_data_cleansed)

            for i in range(len(voices_eng)):
                voices_eng[i] = re.findall(actors_pattern, voices_eng[i])
                voices_eng[i] = " ".join(voices_eng[i])

            profile_data["actors"]["voices_eng"] = voices_eng

        elif row_header == "Drama actor":

            drama_actors = re.split(br_split_pattern, row_data_cleansed)

            for i in range(len(drama_actors)):
                drama_actors[i] = re.findall(actors_pattern, drama_actors[i])
                drama_actors[i] = " ".join(drama_actors[i])

            profile_data["actors"]["drama_actors"] = drama_actors

        profile = Profile(**profile_data)

    return profile

def extract_character_paragraphs(html_string):
    container_div = re.findall(container_div_pattern, html_string)[0]
    container_div_cleansed = re.sub(reference_substitute_pattern, '', container_div)
    container_div_cleansed = re.sub(language_help_substitute_pattern, '', container_div_cleansed)
    
    paragraphs_data = {
        "summary": [],
        "background": [],
        "appearance": [],
        "personality": []
    }

    summary_html = re.findall(summary_pattern, container_div_cleansed)[0]
    summary_paragraphs = re.findall(paragraph_html_extraction_pattern, summary_html)
    summary_paragraphs = ["".join(re.findall(general_data_extraction_pattern, p)) for p in summary_paragraphs if p != ""]
    paragraphs_data["summary"] = summary_paragraphs

    for match in re.finditer(paragraph_with_header_pattern, container_div_cleansed):
        p_header = match.group("p_header")
        p_html = match[0]
        p_texts = re.findall(paragraph_html_extraction_pattern, p_html)
        p_texts = ["".join(re.findall(general_data_extraction_pattern, p)) for p in p_texts if p != ""]
        
        if p_header == "Background":
            paragraphs_data["background"] = p_texts
        
        elif p_header == "Appearance":
            paragraphs_data["appearance"] = p_texts

        elif p_header == "Personality":
            paragraphs_data["personality"] = p_texts
    
    return paragraphs_data

# Weird ass parameter until someone go fetches the page for me
def extract_character(n):
    html_string = read_file(f"../char_test{n}.html")

    profile = extract_character_profile(html_string)
    paragraphs_dict = extract_character_paragraphs(html_string)
    image_urls = extract_image_urls(html_string)
    character = Character(profile=profile, **paragraphs_dict, image_urls=image_urls)
    return character
    