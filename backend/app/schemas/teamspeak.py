from pydantic import BaseModel


class TSClientOut(BaseModel):
    clid: int
    cid: int
    nickname: str


class TSChannelOut(BaseModel):
    cid: int
    pid: int
    name: str
    clients: list[TSClientOut] = []


class TSStatusOut(BaseModel):
    clients: list[TSClientOut]
    channels: list[TSChannelOut]
    client_count: int
    server_host: str
    configured: bool
