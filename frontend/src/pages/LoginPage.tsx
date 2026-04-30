import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { useMe } from '@/hooks/useMe'

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
})

type FormValues = z.infer<typeof schema>

export default function LoginPage() {
  const { data: me, isFetching } = useMe()
  const [sent, setSent] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (isFetching) return null
  if (me) return <Navigate to="/" replace />

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormValues>({
    resolver: zodResolver(schema),
  })

  async function onSubmit({ email }: FormValues) {
    setError(null)
    const { error: apiError } = await apiClient.POST('/auth/request-link', {
      body: { email },
    })
    if (apiError) {
      setError('Something went wrong. Please try again.')
      return
    }
    setSent(true)
  }

  if (sent) {
    return (
      <div className="flex min-h-svh items-center justify-center p-4">
        <div className="w-full max-w-sm text-center space-y-2">
          <h1 className="text-2xl font-semibold">Check your email</h1>
          <p className="text-muted-foreground">
            We sent a magic link to your inbox. Click it to sign in.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-svh items-center justify-center p-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center space-y-1">
          <h1 className="text-2xl font-semibold">Family App</h1>
          <p className="text-muted-foreground">Sign in with your email</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-1">
            <input
              {...register('email')}
              type="email"
              placeholder="you@example.com"
              autoComplete="email"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
            {errors.email && (
              <p className="text-sm text-destructive">{errors.email.message}</p>
            )}
          </div>

          {error && <p className="text-sm text-destructive">{error}</p>}

          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? 'Sending…' : 'Send magic link'}
          </Button>
        </form>
      </div>
    </div>
  )
}
