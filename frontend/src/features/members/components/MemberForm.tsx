import { useEffect } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { memberFormSchema, type MemberFormValues } from '../schemas'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const ROLE_OPTIONS = [
  { value: 'father', label: 'Father' },
  { value: 'mother', label: 'Mother' },
  { value: 'child', label: 'Child' },
  { value: 'sibling', label: 'Sibling' },
  { value: 'unborn', label: 'Baby (unborn)' },
] as const

interface MemberFormProps {
  defaultValues?: Partial<MemberFormValues>
  onSubmit: (values: MemberFormValues) => void
  isSubmitting?: boolean
  submitLabel?: string
}

export function MemberForm({
  defaultValues,
  onSubmit,
  isSubmitting = false,
  submitLabel = 'Save',
}: MemberFormProps) {
  const {
    register,
    control,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm<MemberFormValues>({
    resolver: zodResolver(memberFormSchema),
    defaultValues: defaultValues ?? {},
  })

  // Sync form when defaultValues change (e.g., after data loads on detail page)
  useEffect(() => {
    if (defaultValues) reset(defaultValues)
  }, [defaultValues, reset])

  const role = watch('role')

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="space-y-1.5">
        <Label htmlFor="first_name">First name</Label>
        <Input id="first_name" {...register('first_name')} placeholder="e.g. Sarah" />
        {errors.first_name && (
          <p className="text-sm text-destructive">{errors.first_name.message}</p>
        )}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="nickname">Nickname <span className="text-muted-foreground">(optional)</span></Label>
        <Input id="nickname" {...register('nickname')} placeholder="e.g. Sunny" />
        {errors.nickname && (
          <p className="text-sm text-destructive">{errors.nickname.message}</p>
        )}
      </div>

      <div className="space-y-1.5">
        <Label>Role</Label>
        <Controller
          control={control}
          name="role"
          render={({ field }) => (
            <Select value={field.value} onValueChange={field.onChange}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select a role…" />
              </SelectTrigger>
              <SelectContent>
                {ROLE_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        />
        {errors.role && (
          <p className="text-sm text-destructive">{errors.role.message}</p>
        )}
      </div>

      {role !== 'unborn' && (
        <div className="space-y-1.5">
          <Label htmlFor="birth_date">Birthday <span className="text-muted-foreground">(optional)</span></Label>
          <Input id="birth_date" type="date" {...register('birth_date')} />
        </div>
      )}

      {role === 'unborn' && (
        <div className="space-y-1.5">
          <Label htmlFor="due_date">Due date <span className="text-muted-foreground">(optional)</span></Label>
          <Input id="due_date" type="date" {...register('due_date')} />
        </div>
      )}

      <div className="space-y-1.5">
        <Label htmlFor="email">Email <span className="text-muted-foreground">(optional)</span></Label>
        <Input id="email" type="email" {...register('email')} placeholder="e.g. sarah@family.com" />
        {errors.email && (
          <p className="text-sm text-destructive">{errors.email.message}</p>
        )}
      </div>

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? 'Saving…' : submitLabel}
      </Button>
    </form>
  )
}
