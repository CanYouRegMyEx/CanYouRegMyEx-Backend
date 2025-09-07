from typing import Any, Union

from fastapi import FastAPI
from pydantic import BaseModel

from lib.utils.extract_links import extract_links_asdict
from lib.utils.extract_bgm import BGMData

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None) -> dict[str, Any]:
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item) -> dict[str, Any]:
    return {"item_name": item.name, "item_id": item_id}

@app.get("/list")
def get_list():
    page = ''
    with open('./Anime - Detective Conan Wiki.html', 'r') as f:
        page = f.read()
    return list(extract_links_asdict(page))

@app.get("/bgm")
def get_bgm():
    return BGMData("https://www.detectiveconanworld.com/wiki/Mune_ga_Dokidoki")