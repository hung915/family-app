import { Navigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { useMe } from '@/hooks/useMe'
import { useQueryClient } from '@tanstack/react-query'
import { getErrorMessage } from '@/lib/apiError'

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
})

type FormValues = z.infer<typeof schema>

const inputClass =
  'w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring'

export default function LoginPage() {
  const { data: me } = useMe()
  const queryClient = useQueryClient()
  const { register, handleSubmit, formState: { errors, isSubmitting }, setError } = useForm<FormValues>({
    resolver: zodResolver(schema),
  })

  if (me) return <Navigate to="/" replace />

  async function onSubmit({ email, password }: FormValues) {
    const { data, error: apiError } = await apiClient.POST('/auth/login', {
      body: { email, password },
    })
    if (apiError) {
      setError('root', { message: getErrorMessage(apiError) })
      return
    }
    queryClient.setQueryData(['me'], data)
  }

  return (
    <div className="flex min-h-svh items-center justify-center p-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center space-y-1">
          <h1 className="text-2xl font-semibold">Family App</h1>
          <p className="text-muted-foreground">Sign in to continue</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-1">
            <input
              {...register('email')}
              type="email"
              placeholder="you@example.com"
              autoComplete="email"
              className={inputClass}
            />
            {errors.email && (
              <p className="text-sm text-destructive">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-1">
            <input
              {...register('password')}
              type="password"
              placeholder="Password"
              autoComplete="current-password"
              className={inputClass}
            />
            {errors.password && (
              <p className="text-sm text-destructive">{errors.password.message}</p>
            )}
          </div>

          {errors.root && (
            <p className="text-sm text-destructive">{errors.root.message}</p>
          )}

          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? 'Signing in…' : 'Sign in'}
          </Button>
        </form>
      </div>
    </div>
  )
}
