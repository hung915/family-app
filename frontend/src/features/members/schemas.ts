import { z } from 'zod'

const ROLES = ['father', 'mother', 'child', 'sibling', 'unborn'] as const

export const memberFormSchema = z.object({
  first_name: z.string().min(1, 'Required').max(128, 'Max 128 characters'),
  nickname: z.string().max(64, 'Max 64 characters').optional(),
  role: z.enum(ROLES, { required_error: 'Select a role' }),
  birth_date: z.string().optional(),
  due_date: z.string().optional(),
  email: z
    .union([z.string().email('Enter a valid email'), z.literal('')])
    .optional(),
})

export type MemberFormValues = z.infer<typeof memberFormSchema>
