import { Navigate } from 'react-router-dom'
import { useMe } from '@/hooks/useMe'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { data, isFetching } = useMe()
  if (!data && isFetching) return null
  if (!data) return <Navigate to="/login" replace />
  return <>{children}</>
}
