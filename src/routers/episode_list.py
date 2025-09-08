from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from lib.utils.crawler import crawl
from lib.utils.episode import FilterParams, extract_episodes


EPISODES_PAGE_URL = 'https://www.detectiveconanworld.com/wiki/Anime'


router = APIRouter(prefix='/episodes', tags=['episode_list'])


@router.get('/')
async def get_episodes(filter_params: Annotated[FilterParams, Query()]):
    page = crawl(EPISODES_PAGE_URL)
    if not page:
        raise HTTPException(status_code=500, detail=f'Unable to crawl {EPISODES_PAGE_URL}')
    return extract_episodes(page, filter_params)
