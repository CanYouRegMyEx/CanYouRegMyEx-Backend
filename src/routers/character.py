from lib.utils.extract_character import extract_character, Character
from fastapi import APIRouter, Query

router = APIRouter(prefix='/character', tags=['character'])

@router.get(
    "/",
    summary="Extract a character's information",
    description="Extract information from the character's page on www.detectiveconanworld.com/wiki/ and return as formatted JSON",
    response_model=Character,
)
def extract_character_page(character_page_url: str):
    return extract_character(character_page_url)