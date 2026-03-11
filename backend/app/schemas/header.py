from datetime import datetime

from pydantic import BaseModel


class NextEventOut(BaseModel):
    id: int
    title: str
    start_date: datetime
    type: int
    type_color: str


class HeaderDataOut(BaseModel):
    connected_players: int
    next_events_count: int
    ts_client_count: int
    discord_voice_count: int
    next_events: list[NextEventOut]
