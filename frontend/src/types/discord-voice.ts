export interface DiscordVoiceUser {
  user_id: string
  nickname: string
}

export interface DiscordVoiceChannel {
  channel_id: string
  name: string
  users: DiscordVoiceUser[]
}

export interface DiscordVoiceStatus {
  users: DiscordVoiceUser[]
  channels: DiscordVoiceChannel[]
  user_count: number
  guild_name: string
  configured: boolean
}
