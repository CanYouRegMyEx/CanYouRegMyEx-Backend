from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from lib.utils.crawler import crawl
from lib.utils.extract_episode_list import FilterParams, Plot, extract_episodes, extract_seasons


EPISODES_PAGE_URL = 'https://www.detectiveconanworld.com/wiki/Anime'


router = APIRouter(prefix='/episodes', tags=['episode_list'])


@router.get('/')
async def get_episodes(filter_params: Annotated[FilterParams, Query()]):
    page = crawl(EPISODES_PAGE_URL)
    if not page:
        raise HTTPException(status_code=500, detail=f'Unable to crawl {EPISODES_PAGE_URL}')
    return extract_episodes(page, filter_params)


@router.get('/metadata/seasons')
async def get_metadata_seasons():
    page = crawl(EPISODES_PAGE_URL)
    if not page:
        raise HTTPException(status_code=500, detail=f'Unable to crawl {EPISODES_PAGE_URL}')
    return extract_seasons(page)


@router.get('/metadata/plots')
async def get_metadata_plots():
    return list(map(lambda plot: plot.value, Plot))
