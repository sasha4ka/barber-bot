from fastapi import APIRouter

from book_bot.api.v1.schemas.master import MasterResponse
from book_bot.services.master import get_masters

router = APIRouter(prefix="/masters")


@router.get("", response_model=list[MasterResponse])
async def get_masters_handler():
    return await get_masters()
