from fastapi import APIRouter

from app.config import settings
from app.schemas.discord_voice import DiscordVoiceChannelOut, DiscordVoiceStatusOut, DiscordVoiceUserOut
from app.services import discord_voice as dv_service

router = APIRouter(prefix="/discord-voice", tags=["discord-voice"])


@router.get("/status", response_model=DiscordVoiceStatusOut)
async def get_discord_voice_status():
    if not settings.DISCORD_BOT_TOKEN or not settings.DISCORD_GUILD_ID:
        return DiscordVoiceStatusOut(configured=False)

    data = dv_service.get_cached_status()
    if data is None:
        return DiscordVoiceStatusOut(configured=True)

    users = [DiscordVoiceUserOut(**u) for u in data["users"]]
    channels = [
        DiscordVoiceChannelOut(
            channel_id=ch["channel_id"],
            name=ch["name"],
            users=[DiscordVoiceUserOut(**u) for u in ch["users"]],
        )
        for ch in data["channels"]
    ]
    return DiscordVoiceStatusOut(
        users=users,
        channels=channels,
        user_count=data["user_count"],
        guild_name=data.get("guild_name", ""),
        configured=True,
    )
