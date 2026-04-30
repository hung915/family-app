import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import type { components } from '@/lib/api-types'

export type Me = components['schemas']['MemberResponse']

export function useMe() {
  return useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/auth/me')
      if (error) throw error
      return data
    },
    retry: false,
    staleTime: 1000 * 60 * 10,
  })
}
