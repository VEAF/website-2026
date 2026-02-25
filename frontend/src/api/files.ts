import apiClient from './client'

export interface FileUploadResult {
  id: number
  uuid: string
  type: number
  type_as_string: string | null
  mime_type: string
  size: number
  original_name: string | null
  extension: string
}

export async function uploadFile(file: File): Promise<FileUploadResult> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await apiClient.post<FileUploadResult>('/files', formData)
  return data
}
