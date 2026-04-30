import { QueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { getErrorMessage } from './apiError'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      retry: 1,
    },
    mutations: {
      onError: (error) => {
        toast.error(getErrorMessage(error))
      },
    },
  },
})
