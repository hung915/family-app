import { useState } from 'react'
import { Route, useParams, useNavigate } from 'react-router-dom'
import { useMembers, useCreateMember, useMember, useUpdateMember } from './hooks'
import { MemberCard } from './components/MemberCard'
import { MemberForm } from './components/MemberForm'
import type { MemberFormValues } from './schemas'
import type { MemberCreate, MemberUpdate } from './api'
import { useMe } from '@/hooks/useMe'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'

// ─── Helpers: clean form values before sending to API ────────────────────────
function toCreateBody(values: MemberFormValues): MemberCreate {
  return {
    first_name: values.first_name,
    nickname: values.nickname || null,
    role: values.role,
    birth_date: values.birth_date || null,
    due_date: values.due_date || null,
    email: values.email || null,
  }
}

function toUpdateBody(values: MemberFormValues): MemberUpdate {
  return {
    first_name: values.first_name,
    nickname: values.nickname || null,
    role: values.role,
    birth_date: values.birth_date || null,
    due_date: values.due_date || null,
    email: values.email || null,
  }
}

// ─── List page (/members) ─────────────────────────────────────────────────────
function MembersListPage() {
  const { data: members, isLoading, error } = useMembers()
  const { data: me } = useMe()
  const { mutate: createMember, isPending: isCreating } = useCreateMember()
  const [dialogOpen, setDialogOpen] = useState(false)

  const canAdd = me?.role === 'father' || me?.role === 'mother'

  if (isLoading) {
    return <p className="p-8 text-muted-foreground">Loading…</p>
  }

  if (error) {
    return <p className="p-8 text-destructive">Failed to load members.</p>
  }

  return (
    <div className="mx-auto max-w-lg px-4 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Family</h1>
        {canAdd && (
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button size="sm">Add member</Button>
            </DialogTrigger>
            <DialogContent className="max-w-sm">
              <DialogHeader>
                <DialogTitle>Add family member</DialogTitle>
              </DialogHeader>
              <MemberForm
                submitLabel="Add member"
                isSubmitting={isCreating}
                onSubmit={(values) => {
                  createMember(toCreateBody(values), {
                    onSuccess: () => setDialogOpen(false),
                  })
                }}
              />
            </DialogContent>
          </Dialog>
        )}
      </div>

      {members && members.length === 0 ? (
        <p className="text-muted-foreground text-sm">No members yet.</p>
      ) : (
        <div className="space-y-2">
          {members?.map((member) => (
            <MemberCard key={member.id} member={member} />
          ))}
        </div>
      )}
    </div>
  )
}

// ─── Detail page (/members/:id) ───────────────────────────────────────────────
function MemberDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: member, isLoading, error } = useMember(id!)
  const { mutate: updateMember, isPending: isUpdating } = useUpdateMember()

  if (isLoading) {
    return <p className="p-8 text-muted-foreground">Loading…</p>
  }

  if (error || !member) {
    return (
      <div className="mx-auto max-w-lg px-4 py-8 space-y-4">
        <Button variant="ghost" size="sm" onClick={() => navigate('/members')}>
          ← Back
        </Button>
        <p className="text-destructive">Member not found.</p>
      </div>
    )
  }

  const defaultValues: MemberFormValues = {
    first_name: member.first_name,
    nickname: member.nickname ?? '',
    role: member.role,
    birth_date: member.birth_date ?? '',
    due_date: member.due_date ?? '',
    email: member.email ?? '',
  }

  return (
    <div className="mx-auto max-w-lg px-4 py-8 space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => navigate('/members')}>
          ← Back
        </Button>
        <h1 className="text-2xl font-semibold">{member.first_name}</h1>
      </div>

      <MemberForm
        defaultValues={defaultValues}
        submitLabel="Save changes"
        isSubmitting={isUpdating}
        onSubmit={(values) => {
          updateMember({ id: id!, body: toUpdateBody(values) })
        }}
      />
    </div>
  )
}

// ─── Route definitions ────────────────────────────────────────────────────────
export const membersRoutes = (
  <>
    <Route path="/members" element={<MembersListPage />} />
    <Route path="/members/:id" element={<MemberDetailPage />} />
  </>
)
