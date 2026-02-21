from datetime import datetime

from pydantic import BaseModel


class ServerOut(BaseModel):
    id: int
    name: str
    code: str
    atc: bool
    gci: bool

    model_config = {"from_attributes": True}


class PlayerOut(BaseModel):
    id: int
    ucid: str
    nickname: str | None = None
    join_at: datetime | None = None
    last_join_at: datetime | None = None
    user_nickname: str | None = None

    model_config = {"from_attributes": True}
