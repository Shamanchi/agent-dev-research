"""Эндпоинты корпуса и брифа."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.services.research import DevBrief, ScoredDoc, build_brief, search_docs

router = APIRouter()


class BriefRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    max_docs: int = Field(default=3, ge=1, le=10)


@router.get("/corpus", response_model=list[ScoredDoc])
async def corpus(
    q: str = "",
    max_docs: int = 5,
    settings: Settings = Depends(get_settings),
) -> list[ScoredDoc]:
    try:
        return search_docs(q, max_docs, settings.min_score)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/brief", response_model=DevBrief)
async def brief(
    request: BriefRequest,
    settings: Settings = Depends(get_settings),
) -> DevBrief:
    try:
        return build_brief(request.query, request.max_docs, settings.min_score)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
