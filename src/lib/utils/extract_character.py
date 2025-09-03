import re
from typing import List, Dict

class Profile:
    def __init__(
            self, 
            name_eng: str, 
            surname_eng: str, 
            name_jpn: str, 
            surname_jpn: str, 
            age: str,
            gender: str, 
            height: str, 
            weight: str, 
            birthday: str,
            occupations: str, 
            actors: Dict[str, List[str]]
        ):

        self.name_eng = name_eng
        self.surname_eng = surname_eng
        self.name_jpn = name_jpn
        self.surname_jpn = surname_jpn
        self.age = age
        self.gender = gender
        self.height = height
        self.weight = weight
        self.birthday = birthday
        # self.statuses = # Alive/Dead, for factual status and sometimes as perceived from another party
        self.occupations = occupations
        self.actors = actors
    
    def to_dict(self):
        return {
            "name_eng": self.name_eng,
            "surname_eng": self.surname_eng,
            "name_jpn": self.name_jpn,
            "surname_jpn": self.surname_jpn,
            "gender": self.gender,
            "height": self.height,
            "weight": self.weight,
            "occupations": self.occupations,
            "actors": self.actors
        }
    
class Character:
    def __init__(self, profile: Profile, summary: str, background: str, appearance: str, personality: str):
        self.profile = profile
        self.summary = summary
        self.background = background
        self.appearance = appearance
        self.personality = personality

    def to_dict(self):
        return {
            "profile": self.profile.to_dict(),
            "summary": self.summary,
            "background": self.background,
            "appearance": self.appearance,
            "personality": self.personality
        }

profile_table_pattern = re.compile(r'<table class="infobox"[^>]*>.*?</table>', re.DOTALL)
profile_table_rows_pattern = re.compile(r'<tr>\s*<th>(?P<row_header>[^<]+:)\s*</th>\s*<td>(?P<row_data>[^\n]*)\n</td></tr>', re.DOTALL)

def read_file(file_path):
    with open(file_path, 'r', encoding="utf-8") as f:
        return f.read()

# Fake ass parameter until someone go fetches the page for me
def extract_character(html_string):
    html = read_file("char_test.html")
    profile_table = re.findall(profile_table_pattern, html)
    
    # =============== Profile Parsing ===============
    profile_data = {
        "name_eng": "", "surname_eng": "", "name_jpn": "", "surname_jpn": "", "age": "",
        "gender": "", "height": "", "weight": "", "birthday": "", "occupations": [], "actors": {}
    }

    for match in re.finditer(profile_table_rows_pattern, profile_table[0]):
        row_header = match.group('row_header')
        row_data = match.group('row_data')
        
        if row_header == "Japanese name:":
            full_name_jpn, romanji = row_data.split(" <br /> ")     #TODO: cast to int when this shit is parsed correctly
            name_jpn, surname_jpn = full_name_jpn.split()
            profile_data["name_jpn"] = name_jpn
            profile_data["surname_jpn"] = surname_jpn

        elif row_header == "English name:":
            name_eng, surname_eng = row_data.split()                #TODO: cast to int when this shit is parsed correctly
            profile_data["name_eng"] = name_eng
            profile_data["surname_eng"] = surname_eng
        
        elif row_header == "Age:":
            profile_data["age"] = row_data                          #TODO: cast to int when this shit is parsed correctly
        
        elif row_header == "Height:":
            profile_data["height"] = row_data
        
        elif row_header == "Weight":
            profile_data["weight"] = row_data

        elif row_header == "Date of birth:":
            profile_data["birthday"] = row_data

        elif row_header == "Occupation:":
            profile_data["occupations"] = row_data.split(" <br /> ")    #TODO: parse this shit with RegEx later

        # elif row_header == "Status:":
        #     pass

        elif row_header == "Japanese voice:":
            voices_jpn = row_data.split(" <br /> ")                #TODO: parse this shit with RegEx later
            profile_data["actors"]["voices_jp"] = voices_jpn

        elif row_header == "English voice:":
            voices_eng = row_data.split(" <br /> ")                #TODO: parse this shit with RegEx later
            profile_data["actors"]["voices_eng"] = voices_eng

        elif row_header == "Drama actor:":
            drama_actors = row_data.split(" <br /> ")                #TODO: parse this shit with RegEx later
            profile_data["actors"]["drama_actors"] = drama_actors

    profile = Profile(**profile_data)
    
    return profile