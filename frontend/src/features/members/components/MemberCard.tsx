import { Link } from 'react-router-dom'
import { cn } from '@/lib/utils'
import type { Member, MemberRole } from '../api'

const ROLE_STYLES: Record<MemberRole, string> = {
  father: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
  mother: 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300',
  child: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300',
  sibling: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
  unborn: 'bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-300',
}

const ROLE_LABELS: Record<MemberRole, string> = {
  father: 'Father',
  mother: 'Mother',
  child: 'Child',
  sibling: 'Sibling',
  unborn: 'Baby',
}

interface MemberCardProps {
  member: Member
}

export function MemberCard({ member }: MemberCardProps) {
  return (
    <Link
      to={`/members/${member.id}`}
      className="flex items-center gap-4 rounded-xl border border-border bg-card p-4 transition-colors hover:bg-muted/50"
    >
      <div className="shrink-0">
        {member.avatar_url ? (
          <img
            src={member.avatar_url}
            alt=""
            className="size-14 rounded-full object-cover"
          />
        ) : (
          <div className="size-14 rounded-full bg-muted flex items-center justify-center text-xl font-semibold text-muted-foreground select-none">
            {member.first_name[0].toUpperCase()}
          </div>
        )}
      </div>

      <div className="min-w-0 flex-1">
        <p className="font-medium text-foreground truncate">{member.first_name}</p>
        {member.nickname && (
          <p className="text-sm text-muted-foreground truncate">"{member.nickname}"</p>
        )}
      </div>

      <span
        className={cn(
          'shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium',
          ROLE_STYLES[member.role],
        )}
      >
        {ROLE_LABELS[member.role]}
      </span>
    </Link>
  )
}
