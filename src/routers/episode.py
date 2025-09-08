from typing import Annotated
from fastapi import APIRouter, Query
from lib.utils.episode import FilterParams, extract_episodes


router = APIRouter(prefix='/episode', tags=['episode'])


@router.get('/')
async def get_episodes(filter_params: Annotated[FilterParams, Query()]):
    wikipage = ''

    with open('./Anime - Detective Conan Wiki.html', 'r') as f:
        wikipage = f.read()

    return extract_episodes(wikipage, filter_params)
