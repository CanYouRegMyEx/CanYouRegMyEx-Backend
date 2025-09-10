import re
import urllib.request
import urllib.parse

class BGMData:
    def __init__(self, target_url):
        self.metadata = None
        self.description = None
        self.gallery = None
        self.extract(target_url)

    def extract(self, target_url):
        BGMImage.hostname = urllib.parse.urlparse(target_url).netloc
        response = urllib.request.urlopen(target_url)
        html = response.read().decode("UTF-8")
        self.metadata = BGMMetadata().extract(html)
        self.description = BGMDescription().extract(html)
        self.gallery = BGMImageGallery().extract(html)

class BGMMetadata:
    romanji_title_pattern = re.compile(r'<h1 id="firstHeading" class="firstHeading" lang="en">(.*?)</h1>', re.DOTALL)
    table_pattern = re.compile(r'<table class="infobox".*?>.*?</table>', re.DOTALL)
    table_row_pattern = re.compile(r"<th.*?>(.*?)</th>.*?<td.*?>(.*?)</td>", re.DOTALL)
    data_pattern = re.compile(r"(?:>|^)([^<>\n]+)(?:<|$)", re.DOTALL)
    meta_image_url_pattern = re.compile(r'<img.*?src="(.*?)".*?>', re.DOTALL)

    def __init__(self):
        self.meta_image = None
        self.original_title = None
        self.romanji_title = None
        self.english_title = None
        self.artist = None
        self.episodes = None

    def extract(self, html):
        romanji_title = re.search(BGMMetadata.romanji_title_pattern, html)
        bgm_metadata_table = re.search(BGMMetadata.table_pattern, html)
        table_row_data = re.findall(BGMMetadata.table_row_pattern, bgm_metadata_table.group())
        meta_image_url = re.search(BGMMetadata.meta_image_url_pattern, bgm_metadata_table.group())
        extracted_data = {key.lower().strip().strip(":").replace(" ", "_") : "".join(re.findall(BGMMetadata.data_pattern, data)) for key, data in table_row_data}
        if "episodes" in extracted_data:
            extracted_data["episodes"] = {key : value for key, value in  zip(("japan", "united_state"), extracted_data["episodes"].strip().split(" "))}
        self.meta_image = BGMImage(meta_image_url.group(1))
        self.romanji_title = romanji_title.group(1)
        for key, data in extracted_data.items():
            if key in self.__dict__:
                self.__dict__[key] = data
        return self

class BGMDescription:
    description_section_pattern = re.compile(r'<table class="infobox".*?>.*?</table>.*?<p>(.*?)</p>', re.DOTALL)
    data_pattern = re.compile(r'(?:>|^)([^<>\n]+)(?:<|$)', re.DOTALL)
    cast_section_pattern = re.compile(r'<span class="mw-headline" id="Cast">Cast</span>.*?<span.*?>', re.DOTALL)
    cast_image_pattern = re.compile(r'<img.*?src="(.*?)".*?>.*?<a.*?>(.*?)</a>', re.DOTALL)
    speech_section_pattern = re.compile(r'<span class="mw-headline" id="Conan.27s_opening_speech">Conan\'s opening speech</span>.*?<span class="mw-headline" id="Song_[Ii]nfo">Song [Ii]nfo</span>', re.DOTALL)
    speech_section_by_language_pattern = re.compile(r'<h4>(.*?)</h4>.*?<table.*?>(.*?)</table>', re.DOTALL)
    speech_block_pattern = re.compile(r'<td.*?>.*?<td.*?>(.*?)</td>.*?</td>', re.DOTALL)
    speech_data_pattern = re.compile(r'(?:>|^|\n)([^<>\n]+)(?:<|$|\n)', re.DOTALL)
    alternate_speech_section_pattern = re.compile(r'<table.*?>(.*?)</table>', re.DOTALL)
    lyrics_section_pattern = re.compile(r'<span class="mw-headline" id="Lyrics">Lyrics</span>.*?<span.*?>', re.DOTALL)
    lyrics_section_by_language_pattern = re.compile(r'<div.*?data-title="(.*?)".*?>(.*?)</div>', re.DOTALL)
    cd_info_section_pattern = re.compile(r'(?:<span class="mw-headline" id="CD_[Ii]nfo">CD [Ii]nfo</span>).*?<span class="mw-headline" id="Gallery">Gallery</span>|(?:<span class="mw-headline" id="Release_info">Release info</span>).*?<span class="mw-headline" id="Gallery">Gallery</span>', re.DOTALL)
    alternate_cd_info_section_pattern = re.compile(r'<span class="mw-headline" id="CD_Track_Listing">CD Track Listing</span>.*?(?:<span class="mw-headline" id="Gallery">Gallery</span>)|<span class="mw-headline" id="CD_Track_Listing">CD Track Listing</span>.*?(?:<span class="mw-headline" id="See_also">See also</span>)', re.DOTALL)
    cd_info_cd_tracks_section_pattern = re.compile(r'(?:<h3>.*?<span.*?>(.*?)</span></h3>)?.*?<table.*?>(.*?)</table>', re.DOTALL)
    cd_info_row_pattern = re.compile(r'<tr>(.*?)</tr>', re.DOTALL)
    cd_info_data_pattern = re.compile(r'<td.*?>(.*?)\n?</td>', re.DOTALL)

    def __init__(self):
        self.description = None
        self.cast = []
        self.speech = {}
        self.lyrics = None
        self.cd_info = None

    def extract(self, html):
        description_section = re.search(BGMDescription.description_section_pattern, html)
        description_data = re.findall(BGMDescription.data_pattern, description_section.group(1))
        cast_section = re.search(BGMDescription.cast_section_pattern, html)
        if cast_section != None:
            cast_images = re.findall(BGMDescription.cast_image_pattern, cast_section.group())
            self.cast = [BGMImage(*image) for image in cast_images]
        speech_section = re.search(BGMDescription.speech_section_pattern, html)
        if speech_section != None:
            speech_section_by_language = re.findall(BGMDescription.speech_section_by_language_pattern, speech_section.group())
            if speech_section_by_language != []:
                speech_data_raw = [(language, re.search(BGMDescription.speech_block_pattern, speech).group(1)) for language, speech in speech_section_by_language]
                speech_data = {"".join(re.findall(BGMDescription.data_pattern, language)) : "".join(re.findall(BGMDescription.speech_data_pattern, speech)) for language, speech in speech_data_raw}
            else:
                alternate_speech_section = re.search(BGMDescription.alternate_speech_section_pattern, speech_section.group())
                speech_data_raw = re.search(BGMDescription.speech_block_pattern, alternate_speech_section.group(1))
                speech_data = {"Japanese" : "".join(re.findall(BGMDescription.speech_data_pattern, speech_data_raw.group(1)))}
            self.speech = speech_data
        lyrics_section = re.search(BGMDescription.lyrics_section_pattern, html)
        if lyrics_section != None:
            lyrics_section_by_language = re.findall(BGMDescription.lyrics_section_by_language_pattern, lyrics_section.group())
            lyrics_data = {language : " ".join(re.findall(BGMDescription.data_pattern, lyric)) for language, lyric in lyrics_section_by_language}
            self.lyrics = lyrics_data
        cd_info_section = re.search(BGMDescription.cd_info_section_pattern, html)
        if cd_info_section != None:
            cd_info_cd_tracks = re.findall(BGMDescription.cd_info_cd_tracks_section_pattern, cd_info_section.group())
            cd_info_row = [(track_name, re.findall(BGMDescription.cd_info_row_pattern, cd_info_table)) for track_name, cd_info_table in cd_info_cd_tracks]
            cd_info_data = [("".join(re.findall(BGMDescription.data_pattern, track_name)), [["".join(re.findall(BGMDescription.data_pattern, data)) for data in re.findall(BGMDescription.cd_info_data_pattern, row)] for row in rows[1:]]) for track_name, rows in cd_info_row]
        else:
            alternate_cd_info_section = re.search(BGMDescription.alternate_cd_info_section_pattern, html)
            cd_info_cd_tracks = re.findall(BGMDescription.cd_info_cd_tracks_section_pattern, alternate_cd_info_section.group())
            cd_info_row = [(track_name, re.findall(BGMDescription.cd_info_row_pattern, cd_info_table)) for track_name, cd_info_table in cd_info_cd_tracks]
            cd_info_data = [("".join(re.findall(BGMDescription.data_pattern, track_name)), [["".join(re.findall(BGMDescription.data_pattern, data)) for data in re.findall(BGMDescription.cd_info_data_pattern, row)] for row in rows[1:]]) for track_name, rows in cd_info_row]
        self.cd_info = {track_name : [BGMCD(*cd_info) for cd_info in cd_infos] for track_name, cd_infos in cd_info_data}
        self.description = "".join(description_data)
        
        return self

class BGMImageGallery:
    image_gallery_section_pattern = re.compile(r'<h[23]><span class="mw-headline" id="Gallery">Gallery</span></h[23]>\n?(.*?)<h2>.*?<span.*?>.*?</span>.*?</h2>', re.DOTALL)
    cd_tv_other_divider_pattern = re.compile(r'(?:<h[34]>(.*?)<h[34]>(.*))|(.*)', re.DOTALL)
    image_pattern = re.compile(r'<img.*?src="(.*?)".*?>(?:.*?<div.*?class="gallerytext".*?>(.*?)</div>)?', re.DOTALL)
    data_pattern = re.compile(r'<.*?>', re.DOTALL)

    def __init__(self):
        self.cd = []
        self.tv = []
        self.other = []

    def extract(self, html):
        gallery_section = re.search(BGMImageGallery.image_gallery_section_pattern, html)
        if gallery_section == None:
            return self
        cd_tv_other_section = re.search(BGMImageGallery.cd_tv_other_divider_pattern, gallery_section.group(1))
        cd_section, tv_section, other_section = cd_tv_other_section.group(1, 2, 3)
        if cd_section != None:
            cd_section_image = [(image_url, re.sub(BGMImageGallery.data_pattern, r'', caption).strip()) for image_url, caption in re.findall(BGMImageGallery.image_pattern, cd_section)]
            self.cd = [BGMImage(*image) for image in cd_section_image]
        if tv_section != None:
            tv_section_image = [(image_url, re.sub(BGMImageGallery.data_pattern, r'', caption).strip()) for image_url, caption in re.findall(BGMImageGallery.image_pattern, tv_section)]
            self.tv = [BGMImage(*image) for image in tv_section_image]
        if other_section != None:
            other_section_image = [(image_url, re.sub(BGMImageGallery.data_pattern, r'', caption).strip()) for image_url, caption in re.findall(BGMImageGallery.image_pattern, other_section)]
            self.other = [BGMImage(*image) for image in other_section_image]
        return self

class BGMImage:
    hostname = None

    def __init__(self, image_url, caption=""):
        self.image_url = BGMImage.hostname + image_url
        self.caption = caption

class BGMCD:
    def __init__(self, number, japanese_title, romanji_title, translated_title, length):
        self.number = number
        self.japanese_title = japanese_title
        self.romanji_title = romanji_title
        self.translated_title = translated_title
        self.length = length