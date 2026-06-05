from pydantic import BaseModel


class MasterResponse(BaseModel):
    id: int
    username: str
    full_name: str


class CreateMasterRequest(BaseModel):
    username: str
    password: str
    full_name: str
    tg_id: int | None = None


class UpdateMasterPasswordRequest(BaseModel):
    new_password: str


class MasterLoginRequest(BaseModel):
    username: str
    password: str


class MasterLoginResponse(BaseModel):
    bearer_token: str
