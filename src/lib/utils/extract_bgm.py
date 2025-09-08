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
    table_row_pattern = re.compile(r"<td.*?>(.*?)</td>", re.DOTALL)
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
        meta_image_url = re.search(BGMMetadata.meta_image_url_pattern, table_row_data[1])
        extracted_data = [re.findall(BGMMetadata.data_pattern, data) for data in table_row_data]
        self.meta_image = BGMImage(meta_image_url.group(1))
        self.original_title = extracted_data[3][0]
        self.romanji_title = romanji_title.group(1)
        self.english_title = extracted_data[4][0]
        self.artist = extracted_data[5][0]
        self.episodes = [data for data in extracted_data[6] if data != " "]
        return self

class BGMDescription:
    description_section_pattern = re.compile(r'<table class="infobox".*?>.*?</table>.*?<p>(.*?)</p>', re.DOTALL)
    data_pattern = re.compile(r'(?:>|^)([^<>\n]+)(?:<|$)', re.DOTALL)
    cast_section_pattern = re.compile(r'<span class="mw-headline" id="Cast">Cast</span>.*?<span.*?>', re.DOTALL)
    cast_image_pattern = re.compile(r'<img.*?src="(.*?)".*?>.*?<a.*?>(.*?)</a>', re.DOTALL)
    speech_section_pattern = re.compile(r'<span class="mw-headline" id="Conan.27s_opening_speech">Conan\'s opening speech</span>.*?<span class="mw-headline" id="Song_info">Song info</span>', re.DOTALL)
    speech_section_by_language_pattern = re.compile(r'<h4>(.*?)</h4>.*?<table.*?>(.*?)</table>', re.DOTALL)
    speech_block_pattern = re.compile(r'<td.*?>.*?<td.*?>(.*?)</td>.*?</td>', re.DOTALL)
    speech_data_pattern = re.compile(r'(?:>|^|\n)([^<>\n]+)(?:<|$|\n)', re.DOTALL)
    lyrics_section_pattern = re.compile(r'<span class="mw-headline" id="Lyrics">Lyrics</span>.*?<span.*?>', re.DOTALL)
    lyrics_section_by_language_pattern = re.compile(r'<div.*?data-title="(.*?)".*?>(.*?)</div>', re.DOTALL)
    cd_info_section_pattern = re.compile(r'<span class="mw-headline" id="CD_[Tt]rack_[Ll]isting">CD [Tt]rack [Ll]isting</span>.*?<span class="mw-headline" id="Gallery">Gallery</span>', re.DOTALL)
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
        cast_images = re.findall(BGMDescription.cast_image_pattern, cast_section.group())
        speech_section = re.search(BGMDescription.speech_section_pattern, html)
        if speech_section != None:
            speech_section_by_language = re.findall(BGMDescription.speech_section_by_language_pattern, speech_section.group())
            speech_data_raw = [(language, re.search(BGMDescription.speech_block_pattern, speech).group(1)) for language, speech in speech_section_by_language]
            speech_data = {"".join(re.findall(BGMDescription.data_pattern, language)) : "".join(re.findall(BGMDescription.speech_data_pattern, speech)) for language, speech in speech_data_raw}
            self.speech = speech_data
        lyrics_section = re.search(BGMDescription.lyrics_section_pattern, html)
        lyrics_section_by_language = re.findall(BGMDescription.lyrics_section_by_language_pattern, lyrics_section.group())
        lyrics_data = {language : "".join(re.findall(BGMDescription.data_pattern, lyric)) for language, lyric in lyrics_section_by_language}
        cd_info_section = re.search(BGMDescription.cd_info_section_pattern, html)
        cd_info_row = re.findall(BGMDescription.cd_info_row_pattern, cd_info_section.group())
        cd_info_data = [re.findall(BGMDescription.cd_info_data_pattern, row) for row in cd_info_row[1:]]
        self.description = "".join(description_data)
        self.cast = [BGMImage(*image) for image in cast_images]
        self.lyrics = lyrics_data
        self.cd_info = [BGMCD(*cd_info) for cd_info in cd_info_data]
        return self

class BGMImageGallery:
    image_gallery_section_pattern = re.compile(r'<h2><span class="mw-headline" id="Gallery">Gallery</span></h2>\n?(.*?)<h2>.*?<span.*?>.*?</span>.*?</h2>', re.DOTALL)
    cd_tv_other_divider_pattern = re.compile(r'(?:<h3>(.*?)<h3>(.*))|(.*)', re.DOTALL)
    image_pattern = re.compile(r'<img.*?src="(.*?)".*?>.*?<div.*?class="gallerytext".*?>(.*?)</div>', re.DOTALL)
    data_pattern = re.compile(r'(?:>|^)([^<>\n]+)(?:<|$)', re.DOTALL)

    def __init__(self):
        self.cd = []
        self.tv = []

    def extract(self, html):
        gallery_section = re.search(BGMImageGallery.image_gallery_section_pattern, html)
        cd_tv_other_section = re.search(BGMImageGallery.cd_tv_other_divider_pattern, gallery_section.group(1))
        cd_section, tv_section, other_section = cd_tv_other_section.group(1, 2, 3)
        print(re.findall(BGMImageGallery.image_pattern, cd_section))
        cd_section_image = [(image_url, "".join(re.findall(BGMImageGallery.data_pattern, caption))) for image_url, caption in re.findall(BGMImageGallery.image_pattern, cd_section)]
        tv_section_image = [(image_url, "".join(re.findall(BGMImageGallery.data_pattern, caption))) for image_url, caption in re.findall(BGMImageGallery.image_pattern, tv_section)]
        if other_section != None:
            other_section_image = [(image_url, "".join(re.findall(BGMImageGallery.data_pattern, caption))) for image_url, caption in re.findall(BGMImageGallery.image_pattern, other_section)]
        else:
            other_section_image = []
        self.cd = [BGMImage(*image) for image in cd_section_image + other_section_image]
        self.tv = [BGMImage(*image) for image in tv_section_image]
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

bgm = BGMData("https://www.detectiveconanworld.com/wiki/Mune_ga_Dokidoki")