from typing import Annotated
from fastapi import APIRouter, Query
from lib.utils.extract_episode import main_extract_episode


router = APIRouter(prefix='/episode', tags=['episode'])


@router.get('/extract')
async def extract_episode_page(episode_url: str):

    return main_extract_episode(episode_url)
