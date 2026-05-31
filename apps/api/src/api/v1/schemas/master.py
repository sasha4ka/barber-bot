from pydantic import BaseModel


class MasterResponse(BaseModel):
    id: int
    full_name: str
