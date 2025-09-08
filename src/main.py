from typing import Any, Union

from fastapi import FastAPI
from pydantic import BaseModel

from routers import episode_list, episode
from lib.utils.extract_character import extract_character, Character

app = FastAPI()

app.include_router(episode_list.router)
app.include_router(episode.router)

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

@app.get(
    "/extract_character",
    summary="Extract a character's information",
    description="Extract information from the character's page on www.detectiveconanworld.com/wiki/ and return as formatted JSON",
    response_model=Character,
)
def extract_character_page(character_page_url: str):
    return extract_character(character_page_url)


