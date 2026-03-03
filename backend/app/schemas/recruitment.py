from datetime import datetime

from pydantic import BaseModel, Field


class AdminRecruitmentEventOut(BaseModel):
    id: int
    type: int
    type_as_string: str
    event_at: datetime | None = None
    comment: str | None = None
    ack_at: datetime | None = None
    user_id: int
    user_nickname: str | None = None
    validator_id: int | None = None
    validator_nickname: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class AdminRecruitmentEventListOut(BaseModel):
    items: list[AdminRecruitmentEventOut] = Field(default_factory=list)
    total: int


class AdminRecruitmentEventUpdate(BaseModel):
    comment: str | None = Field(None, max_length=255)
    event_at: datetime | None = None
