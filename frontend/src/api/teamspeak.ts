import apiClient from './client'
import type { TSStatus } from '@/types/teamspeak'

export async function getTeamSpeakStatus(): Promise<TSStatus> {
  const { data } = await apiClient.get<TSStatus>('/teamspeak/status')
  return data
}
