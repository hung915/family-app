import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from './api'
import type { MemberCreate, MemberUpdate } from './api'

// ─── Cache key factory ───────────────────────────────────────────────────────
export const MEMBER_KEYS = {
  all: ['members'] as const,
  detail: (id: string) => ['members', id] as const,
}

// ─── Queries ─────────────────────────────────────────────────────────────────
export function useMembers() {
  return useQuery({
    queryKey: MEMBER_KEYS.all,
    queryFn: api.fetchMembers,
  })
}

export function useMember(id: string) {
  return useQuery({
    queryKey: MEMBER_KEYS.detail(id),
    queryFn: () => api.fetchMember(id),
    enabled: !!id,
  })
}

// ─── Mutations ───────────────────────────────────────────────────────────────
export function useCreateMember() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: MemberCreate) => api.createMember(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: MEMBER_KEYS.all })
    },
  })
}

export function useUpdateMember() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: MemberUpdate }) =>
      api.updateMember(id, body),
    onSuccess: (_data, { id }) => {
      queryClient.invalidateQueries({ queryKey: MEMBER_KEYS.all })
      queryClient.invalidateQueries({ queryKey: MEMBER_KEYS.detail(id) })
    },
  })
}

export function useDeleteMember() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.deleteMember(id),
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: MEMBER_KEYS.all })
      queryClient.removeQueries({ queryKey: MEMBER_KEYS.detail(id) })
    },
  })
}
