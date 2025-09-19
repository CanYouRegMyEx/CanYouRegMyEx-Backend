from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, Response
from lib.utils.extract_episode_list import FilterParams
from lib.utils.crawler import crawl
from lib.utils.export_file import export_csv, export_json
from lib.utils.extract_episode_list import extract_episodes

EPISODES_PAGE_URL = 'https://www.detectiveconanworld.com/wiki/Anime'

router = APIRouter(prefix='/export_file', tags=['export_file'])

@router.get('/get_csv')
async def get_csv():
    page = crawl(EPISODES_PAGE_URL)
    if not page:
        raise HTTPException(status_code=500, detail=f'Unable to crawl {EPISODES_PAGE_URL}')
    return export_csv(page)

@router.get('/get_json')
async def get_json():
    page = crawl(EPISODES_PAGE_URL)
    if not page:
        raise HTTPException(status_code=500, detail=f'Unable to crawl {EPISODES_PAGE_URL}')
    return export_json(page)