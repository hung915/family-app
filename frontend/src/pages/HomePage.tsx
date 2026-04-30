import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'

async function fetchMe() {
  const { data, error } = await apiClient.GET('/auth/me')
  if (error) throw error
  return data
}

async function fetchMembers() {
  const { data, error } = await apiClient.GET('/members')
  if (error) throw error
  return data
}

export default function HomePage() {
  const { data: me } = useQuery({ queryKey: ['me'], queryFn: fetchMe })
  const { data: members } = useQuery({ queryKey: ['members'], queryFn: fetchMembers })

  async function handleLogout() {
    await apiClient.POST('/auth/logout')
    window.location.href = '/login'
  }

  return (
    <div className="min-h-svh p-8 max-w-2xl mx-auto space-y-8">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Family App</h1>
        <div className="flex items-center gap-3">
          {me && <span className="text-sm text-muted-foreground">{me.first_name}</span>}
          <Button variant="outline" size="sm" onClick={handleLogout}>
            Sign out
          </Button>
        </div>
      </header>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">Family</h2>
        {members ? (
          <ul className="divide-y divide-border rounded-lg border">
            {members.map((member) => (
              <li key={member.id} className="flex items-center gap-3 px-4 py-3">
                <div className="size-9 rounded-full bg-muted flex items-center justify-center text-sm font-medium">
                  {member.first_name[0]}
                </div>
                <div>
                  <p className="text-sm font-medium">{member.first_name}</p>
                  <p className="text-xs text-muted-foreground capitalize">{member.role}</p>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted-foreground">Loading…</p>
        )}
      </section>
    </div>
  )
}
