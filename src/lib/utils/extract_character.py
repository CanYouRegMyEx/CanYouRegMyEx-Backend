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
    
class Character:
    def __init__(
            self,
            profile: Profile,
            summary: str,
            background: List[str],
            appearance: List[str],
            personality: List[str],
            skills: List[str],
            image_urls: List[str]
        ):
        
        self.profile = profile
        self.summary = summary
        self.background = background
        self.appearance = appearance
        self.personality = personality
        self.skills = skills
        self.image_urls = image_urls

# Match Patterns - Common
general_data_extraction_pattern = re.compile(r'([^>\n]+)(?=<|\n)', re.DOTALL)

# Match Patterns - Profiles
profile_table_pattern = re.compile(r'<table class="infobox"[^>]*>.*?</table>', re.DOTALL)
profile_table_rows_pattern = re.compile(r'<th[^>]*>(?P<row_header>[^<]+):\s*</th>\s*<td>(?:<^\n+>)?(?P<row_data>[^\n]+)\n</td>', re.DOTALL)
status_extraction_pattern = re.compile(r'\s*([^>\n]+)(?=<|$)', re.DOTALL)
actors_pattern = re.compile(r'\s*([^>\n]+)(?=<|\n|$)', re.DOTALL)

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
br_split_pattern = re.compile(r' <br /> |<br /> | <br />')
nakaten_split_pattern = re.compile(r'・')
space_split_pattern = re.compile(r' ')

# Substitute Patterns
reference_substitute_pattern = re.compile(r'&#\d+;\d+&#\d+;|&#\d+;')
language_help_substitute_pattern = re.compile(r'<span[^>]*>\?<\/span>')
url_substitute_pattern = re.compile(r'(<a.+?>)|(<\/a>)')

def read_file(file_path):
    with open(file_path, 'r', encoding="utf-8") as f:
        return f.read()

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

# Weird ass parameter until someone go fetches the page for me
def extract_character(n):
    html_string = read_file(f"../char_test{n}.html")

    profile = extract_character_profile(html_string)
    paragraphs_dict = extract_character_paragraphs(html_string)
    image_urls = extract_image_urls(html_string)
    character = Character(profile=profile, **paragraphs_dict, image_urls=image_urls[1:10])
    
    return character
    