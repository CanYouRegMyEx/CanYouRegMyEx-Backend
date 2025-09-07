import re
import urllib.request

class GadgetData:
    def __init__(self, target_url):
        self.metadata = None
        self.description = None
        self.gallery = None
        self.extract(target_url)

    def extract(self, target_url):
        response = urllib.request.urlopen(target_url)
        html = response.read().decode("UTF-8")
        self.metadata = GadgetMetadata().extract(html)
        self.description = GadgetDescription().extract(html)
        self.gallery = GadgetImageGallery().extract(html)

class GadgetMetadata:
    table_pattern = re.compile(r'<table class="infobox".*?>.*?</table>', re.DOTALL)
    table_row_pattern = re.compile(r"<td.*?>(.*?)</td>", re.DOTALL)
    data_pattern = re.compile(r"(?:>|^)([^<>\n]+)(?:<|$)", re.DOTALL)
    meta_image_url_pattern = re.compile(r'<img.*?src="(.*?)".*?>', re.DOTALL)
        
    def __init__(self):
        self.meta_image = None
        self.english_name = None
        self.japanese_name = None
        self.romanji_name = None
        self.created_by = None
        self.used_by = None
        self.first_appearance = None
        self.appearances = None

    def extract(self, html):
        gadget_metadata_table = re.search(GadgetMetadata.table_pattern, html)
        table_row_data = re.findall(GadgetMetadata.table_row_pattern, gadget_metadata_table.group())
        meta_image_url = re.search(GadgetMetadata.meta_image_url_pattern, table_row_data[1])
        extracted_data = [re.findall(GadgetMetadata.data_pattern, data) for data in table_row_data]
        self.meta_image = GadgetImage(meta_image_url.group(1))
        self.english_name = extracted_data[0][0]
        self.japanese_name = extracted_data[3][0]
        self.romanji_name = extracted_data[4][0]
        self.created_by = extracted_data[5][0]
        self.used_by = [name for name in extracted_data[6] if name != " "]
        self.first_appearance = extracted_data[8]
        self.appearances = extracted_data[9]
        return self

class GadgetDescription:
    description_section_pattern = re.compile(r'<h2><span class="mw-headline" id="Description">Description</span></h2>.*?<p>(.*?)</p>', re.DOTALL)
    description_data_pattern = re.compile(r"(?:>|^)([^<>\n]+)(?:<|$)", re.DOTALL)
    unique_uses_section_pattern = re.compile(r'<h2><span class="mw-headline" id="Unique_uses">Unique uses</span></h2>.*?<ul>(.*?)</ul>', re.DOTALL)
    unique_uses_list_pattern = re.compile(r"<li>(.*?)</li>", re.DOTALL)
    unique_uses_data_pattern = re.compile(r"(?:>|^)([^<>\n]+)(?:<|$)", re.DOTALL)
    description_image_pattern = re.compile(r'<img.*?src="(.*?)".*?>.*?<div class="thumbcaption">.*?</div>(.*?)</div>', re.DOTALL)

    def __init__(self):
        self.description = None
        self.description_image = []
        self.unique_uses = []

    def extract(self, html):
        description_section = re.search(GadgetDescription.description_section_pattern, html)
        description_data = re.findall(GadgetDescription.description_data_pattern, description_section.group(1))
        description_image = re.findall(GadgetDescription.description_image_pattern, description_section.group())
        description_image = [(image_url, "".join(re.findall(GadgetImageGallery.caption_pattern, caption))) for image_url, caption in description_image]
        self.description = "".join(description_data)
        for image in description_image:
            self.description_image.append(GadgetImage(*image))
        unique_uses_section = re.search(GadgetDescription.unique_uses_section_pattern, html)
        if unique_uses_section != None:
            unique_uses_data_list = re.findall(GadgetDescription.unique_uses_list_pattern, unique_uses_section.group(1))
            unique_uses_data = ["".join(re.findall(GadgetDescription.unique_uses_data_pattern, data_list)) for data_list in unique_uses_data_list]
            self.unique_uses = unique_uses_data
        return self

class GadgetImageGallery:
    gallery_section_pattern = re.compile(r'<h2><span class="mw-headline" id="Gallery">Gallery</span></h2>.*?<h2><span class="mw-headline" id="See_also">See also</span></h2>', re.DOTALL)
    image_pattern = re.compile(r'<img.*?src="(.*?)".*?>.*?<div class="gallerytext">(.*?)</div>', re.DOTALL)
    caption_pattern = re.compile(r"(?:>|^)([^<>\n]+)(?:<|$|\n)", re.DOTALL)

    def __init__(self):
        self.images = []

    def extract(self, html):
        gallery_section = re.search(GadgetImageGallery.gallery_section_pattern, html)
        if gallery_section != None:
            gallery_images = re.findall(GadgetImageGallery.image_pattern, gallery_section.group())
            gallery_images = [(image_url, "".join(re.findall(GadgetImageGallery.caption_pattern, caption))) for image_url, caption in gallery_images]
            for image in gallery_images:
                self.images.append(GadgetImage(*image))
        return self

class GadgetImage:
    def __init__(self, image_url, caption=""):
        self.image_url = image_url
        self.caption = caption

