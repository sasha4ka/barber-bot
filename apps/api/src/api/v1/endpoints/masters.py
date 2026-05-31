from core_shared import AsyncSession
from core_shared.services.master import get_masters
from fastapi import APIRouter, Depends

from api.dependencies import async_session
from api.v1.schemas.master import MasterResponse

router = APIRouter(prefix="/masters")


@router.get("", response_model=list[MasterResponse])
async def get_masters_handler(session: AsyncSession = Depends(async_session)):
    return await get_masters(session=session)
