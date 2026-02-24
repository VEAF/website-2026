export interface TSClient {
  clid: number
  cid: number
  nickname: string
}

export interface TSChannel {
  cid: number
  pid: number
  name: string
  clients: TSClient[]
}

export interface TSStatus {
  clients: TSClient[]
  channels: TSChannel[]
  client_count: number
  server_host: string
  configured: boolean
}
