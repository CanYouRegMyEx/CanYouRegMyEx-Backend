from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from lib.utils.crawler import crawl
from lib.utils.extract_gadget import GadgetData

router = APIRouter(prefix='/gadget', tags=['gadget'])

@router.get("/")
def get_gadget(url: str):
    return GadgetData(url)