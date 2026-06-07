from core_shared import AsyncSession
from core_shared.models import Master
from core_shared.security import JWTAuthenticator
from core_shared.services.master import (
    create_master,
    get_masters,
    update_master_password,
)
from fastapi import APIRouter, Depends

from api.authenticator import get_jwt_authenticator
from api.dependencies import async_session, get_admin, get_current_master
from api.v1.schemas.master import (
    CreateMasterRequest,
    MasterResponse,
    UpdateMasterPasswordRequest,
)

router = APIRouter(prefix="/masters")


@router.get("", response_model=list[MasterResponse])
async def get_masters_handler(
    session: AsyncSession = Depends(async_session),
    master: Master = Depends(get_current_master),
):
    return await get_masters(session=session)


@router.post("", response_model=MasterResponse)
async def create_master_handler(
    model: CreateMasterRequest,
    session: AsyncSession = Depends(async_session),
    master: Master = Depends(get_admin),
):
    return await create_master(
        username=model.username,
        password=model.password,
        full_name=model.full_name,
        tg_id=model.tg_id,
        session=session,
    )


@router.post("/change_password")
async def change_password_handler(
    model: UpdateMasterPasswordRequest,
    session: AsyncSession = Depends(async_session),
    master: Master = Depends(get_current_master),
    jwt: JWTAuthenticator = Depends(get_jwt_authenticator),
):
    await update_master_password(
        master_id=master.id, new_password=model.new_password, session=session
    )
    await jwt.revoke_token(master.id)
    return {"message": "Password updated successfully. You need to relogin"}
