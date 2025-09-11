from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from lib.utils.crawler import crawl
from lib.utils.extract_bgm import BGMData

router = APIRouter(prefix='/bgm', tags=['bgm'])

@router.get("/")
def get_bgm(url: str):
    return BGMData(url)