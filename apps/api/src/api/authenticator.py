from core_shared.security import JWTAuthenticator

from api.database import db
from api.settings import settings

_authenticator: JWTAuthenticator | None = None


def get_jwt_authenticator() -> JWTAuthenticator:
    global _authenticator
    if _authenticator is None:
        raise RuntimeError("JWTAuthenticator is not initialized")
    return _authenticator


def init_jwt_authenticator(secret_key: str, algorithm: str = "HS256"):
    global _authenticator
    if _authenticator is not None:
        raise RuntimeError("JWTAuthenticator is already initialized")
    _authenticator = JWTAuthenticator(
        db=db, secret_key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
