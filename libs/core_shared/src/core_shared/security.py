from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from core_shared.database import Database
from core_shared.exc import JWTAuthenticationError
from core_shared.models import Master
from core_shared.services.master import (
    MasterNotFoundError,
    get_master,
    increment_token_version,
)


class JWTAuthenticator:
    def __init__(self, secret_key: str, db: Database, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.db = db

    async def encode_token(self, master_id: int) -> str:
        async with self.db.session_scope() as session:
            try:
                token_version = await increment_token_version(
                    master_id=master_id, session=session
                )
            except MasterNotFoundError:
                raise JWTAuthenticationError("Master not found")

            payload: dict[str, Any] = {
                "master_id": master_id,
                "token_version": token_version,
                "exp": datetime.now(timezone.utc) + timedelta(days=7),
            }

            return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    async def authenticate(self, token: str) -> Master:
        """Decodes and validates the JWT token. Raises JWTAuthenticationError if token is invalid, expired, or revoked."""
        async with self.db.session_scope() as session:
            try:
                payload = jwt.decode(
                    token, self.secret_key, algorithms=[self.algorithm]
                )
            except jwt.ExpiredSignatureError:
                raise JWTAuthenticationError("Token has expired")
            except jwt.InvalidTokenError:
                raise JWTAuthenticationError("Invalid token")

            master_id = payload.get("master_id")
            token_version = payload.get("token_version")

            if master_id is None or token_version is None:
                raise JWTAuthenticationError("Invalid token payload")

            master = await get_master(master_id=master_id, session=session)

            if master is None:
                raise JWTAuthenticationError("Master not found")

            if master.token_version != token_version:
                raise JWTAuthenticationError("Token has been revoked")

            return master

    async def revoke_token(self, master_id: int) -> None:
        """Revokes master's token by incrementing the token version in the database. Raises JWTAuthenticationError if master not found."""
        try:
            async with self.db.session_scope() as session:
                await increment_token_version(master_id=master_id, session=session)
        except MasterNotFoundError:
            raise JWTAuthenticationError("Master not found")
