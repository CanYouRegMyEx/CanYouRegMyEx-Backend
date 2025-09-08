from typing import Annotated, List
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from lib.utils.episode import Plot


class FilterParams(BaseModel):
    model_config = {"extra": "forbid"}

    filter: List[str] = Field([], max_length=10)
    plot: List[Plot] = Field([], max_length=10)
    season: List[int] = Field([], max_length=10)
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)

router = APIRouter(prefix='/episode', tags=['episode'])


@router.get('/')
async def get_episodes(filter_query: Annotated[FilterParams, Query()]):
    return filter_query
