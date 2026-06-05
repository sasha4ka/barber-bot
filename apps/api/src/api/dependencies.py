from core_shared.exc import JWTAuthenticationError
from core_shared.models import Master
from core_shared.security import JWTAuthenticator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.authenticator import get_jwt_authenticator
from api.database import db

header = HTTPBearer()


async def async_session():
    async with db.session_scope() as session:
        yield session


async def get_current_master(
    auth: HTTPAuthorizationCredentials = Depends(header),
) -> Master:
    authenticator: JWTAuthenticator = get_jwt_authenticator()

    try:
        master = await authenticator.authenticate(token=auth.credentials)
        return master
    except JWTAuthenticationError as er:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(er),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_admin(
    master: Master = Depends(get_current_master),
) -> Master:
    if not master.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return master
