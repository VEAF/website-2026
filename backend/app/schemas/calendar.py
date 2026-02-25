from datetime import datetime

from pydantic import BaseModel, Field


class VoteOut(BaseModel):
    id: int
    user_id: int
    user_nickname: str | None = None
    vote: bool | None = None
    comment: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ChoiceOut(BaseModel):
    id: int
    user_id: int
    user_nickname: str | None = None
    module_id: int
    module_name: str | None = None
    task: int | None = None
    task_as_string: str | None = None
    priority: int
    comment: str | None = None

    model_config = {"from_attributes": True}


class SlotOut(BaseModel):
    id: int
    user_id: int | None = None
    user_nickname: str | None = None
    username: str | None = None

    model_config = {"from_attributes": True}


class FlightOut(BaseModel):
    id: int
    name: str
    mission: str | None = None
    aircraft_id: int
    aircraft_name: str | None = None
    nb_slots: int
    slots: list[SlotOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class EventListOut(BaseModel):
    id: int
    title: str
    start_date: datetime
    end_date: datetime
    type: int
    type_as_string: str | None = None
    type_color: str | None = None
    sim_dcs: bool
    sim_bms: bool
    registration: bool
    owner_nickname: str | None = None

    model_config = {"from_attributes": True}


class EventDetailOut(EventListOut):
    description: str | None = None
    restrictions: list[int] = Field(default_factory=list)
    ato: bool
    debrief: str | None = None
    repeat_event: int
    deleted: bool
    map_id: int | None = None
    map_name: str | None = None
    server_id: int | None = None
    server_name: str | None = None
    image_id: int | None = None
    image_uuid: str | None = None
    owner_id: int
    module_ids: list[int] = Field(default_factory=list)
    module_names: list[str] = Field(default_factory=list)
    restriction_labels: list[str] = Field(default_factory=list)
    votes: list[VoteOut] = Field(default_factory=list)
    choices: list[ChoiceOut] = Field(default_factory=list)
    flights: list[FlightOut] = Field(default_factory=list)


class EventCreate(BaseModel):
    title: str
    start_date: datetime
    end_date: datetime
    type: int
    sim_dcs: bool = False
    sim_bms: bool = False
    description: str | None = None
    restrictions: list[int] = Field(default_factory=list)
    registration: bool = False
    ato: bool = False
    repeat_event: int = 0
    map_id: int | None = None
    server_id: int | None = None
    image_id: int | None = None
    module_ids: list[int] = Field(default_factory=list)


class EventUpdate(EventCreate):
    debrief: str | None = None


class VoteCreate(BaseModel):
    vote: bool | None = None  # True=yes, False=no, None=maybe
    comment: str | None = None


class ChoiceCreate(BaseModel):
    module_id: int
    task: int | None = None
    priority: int = 1
    comment: str | None = None


class ChoiceUpdate(BaseModel):
    module_id: int | None = None
    task: int | None = None
    priority: int | None = None
    comment: str | None = None
