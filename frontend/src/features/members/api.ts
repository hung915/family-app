import { apiClient } from '@/lib/api'
import type { components } from '@/lib/api-types'

export type Member = components['schemas']['MemberResponse']
export type MemberCreate = components['schemas']['MemberCreate']
export type MemberUpdate = components['schemas']['MemberUpdate']
export type MemberRole = components['schemas']['MemberRole']

export async function fetchMembers(): Promise<Member[]> {
  const { data, error } = await apiClient.GET('/members')
  if (error) throw error
  return data
}

export async function fetchMember(id: string): Promise<Member> {
  const { data, error } = await apiClient.GET('/members/{member_id}', {
    params: { path: { member_id: id } },
  })
  if (error) throw error
  return data
}

export async function createMember(body: MemberCreate): Promise<Member> {
  const { data, error } = await apiClient.POST('/members', { body })
  if (error) throw error
  return data
}

export async function updateMember(id: string, body: MemberUpdate): Promise<Member> {
  const { data, error } = await apiClient.PATCH('/members/{member_id}', {
    params: { path: { member_id: id } },
    body,
  })
  if (error) throw error
  return data
}

export async function deleteMember(id: string): Promise<void> {
  const { error } = await apiClient.DELETE('/members/{member_id}', {
    params: { path: { member_id: id } },
  })
  if (error) throw error
}
