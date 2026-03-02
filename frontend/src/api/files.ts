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

// --- Admin File types ---

export interface AdminFile {
  id: number
  uuid: string
  type: number | null
  type_as_string: string | null
  mime_type: string
  size: number
  original_name: string | null
  description: string | null
  extension: string
  created_at: string | null
  owner_id: number | null
  owner_nickname: string | null
}

export interface AdminFileListResponse {
  items: AdminFile[]
  total: number
}

// --- Admin File API functions ---

export async function getAdminFiles(params?: {
  search?: string
  type?: number
  skip?: number
  limit?: number
}): Promise<AdminFileListResponse> {
  const { data } = await apiClient.get<AdminFileListResponse>('/admin/files', { params })
  return data
}

export async function deleteAdminFile(fileId: number): Promise<void> {
  await apiClient.delete(`/admin/files/${fileId}`)
}
