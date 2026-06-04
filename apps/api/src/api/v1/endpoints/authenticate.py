from api.authenticator import JWTAuthenticator, get_jwt_authenticator
from api.dependencies import async_session
from api.v1.schemas.master import MasterLoginRequest, MasterLoginResponse
from core_shared import AsyncSession
from core_shared.exc import PasswordAuthenticationError
from core_shared.services.master import validate_master
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/masters")


@router.post("/login", response_model=MasterLoginResponse)
async def login_master(
    model: MasterLoginRequest,
    jwt: JWTAuthenticator = Depends(get_jwt_authenticator),
    session: AsyncSession = Depends(async_session),
):
    try:
        print(111)
        master = await validate_master(
            username=model.username, password=model.password, session=session
        )
        print(222)
    except PasswordAuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = await jwt.encode_token(master.id)
    return MasterLoginResponse(bearer_token=token)
