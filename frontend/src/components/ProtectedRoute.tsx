import { Navigate } from 'react-router-dom'
import { useMe } from '@/hooks/useMe'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { data, isLoading } = useMe()
  if (isLoading) return null
  if (!data) return <Navigate to="/login" replace />
  return <>{children}</>
}
