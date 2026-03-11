from pydantic import BaseModel, Field


class DiscordVoiceUserOut(BaseModel):
    user_id: str
    nickname: str


class DiscordVoiceChannelOut(BaseModel):
    channel_id: str
    name: str
    users: list[DiscordVoiceUserOut] = Field(default_factory=list)


class DiscordVoiceStatusOut(BaseModel):
    users: list[DiscordVoiceUserOut] = Field(default_factory=list)
    channels: list[DiscordVoiceChannelOut] = Field(default_factory=list)
    user_count: int = 0
    guild_name: str = ""
    configured: bool = False
