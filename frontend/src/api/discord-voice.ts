import apiClient from './client'
import type { DiscordVoiceStatus } from '@/types/discord-voice'

export async function getDiscordVoiceStatus(): Promise<DiscordVoiceStatus> {
  const { data } = await apiClient.get<DiscordVoiceStatus>('/discord-voice/status')
  return data
}
