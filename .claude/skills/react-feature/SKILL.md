---
name: react-feature
description: Scaffold a new feature folder in the React frontend following CLAUDE.md conventions. Use whenever the user asks to add a UI feature (e.g. "build the members UI", "add a pregnancy tracker page", "scaffold the milestones feature"). Produces api.ts, hooks.ts, schemas.ts, components/, routes.tsx, and index.ts under src/features/<domain>/.
---

# Skill: react-feature

## When to use this skill

Use this skill whenever you are asked to create a new UI feature. Triggers include:

- "Add a `<name>` page / screen / UI."
- "Scaffold the frontend for `<thing>`."
- "Build the `<thing>` feature."
- A new backend module just landed and the user asks to wire up its frontend.

Do NOT use this skill for:

- Adding a single component to an existing feature (just edit the existing file).
- Backend work (use the `fastapi-module` skill).
- One-off pages with no server state (create `src/pages/<Name>Page.tsx` directly).

## Inputs to confirm before scaffolding

If any of these are unclear from the conversation, ask **one** clarifying question that bundles them all. Do not ask multiple rounds.

1. **Domain name** — matches the backend module name, lower_snake_case (e.g. `members`, `pregnancy`, `milestones`). The folder is `src/features/<domain>/`.
2. **Backend endpoints that exist** — which operations are available (list, get, create, update, delete)? Only generate calls for endpoints that exist.
3. **Forms needed** — which mutations (create / update) require a user-facing form? Determines what goes in `schemas.ts` and which components to build.
4. **Route paths** — what URL(s) should this feature live at (e.g. `/members`, `/members/:id`)?

## Steps

### 1. Read context first

Before writing anything:

- Read `CLAUDE.md` at the repo root if you haven't already this session.
- Read `frontend/src/lib/api-types.ts` to confirm the available paths, request bodies, and response shapes. **All TypeScript types must come from this file — never hand-write types that duplicate Pydantic schemas.**
- Skim `frontend/src/features/` to see if there is an existing feature to reference for style.
- Skim `frontend/src/App.tsx` to understand how routes are currently wired.

If `api-types.ts` is missing or stale (backend has newer endpoints), run:

```bash
cd frontend && pnpm gen:api
```

### 2. Create the folder and files

Create `frontend/src/features/<domain>/` with these files. Omit a file only if it would genuinely be empty (e.g. no `schemas.ts` if the feature has no forms).

```
frontend/src/features/<domain>/
├── api.ts
├── hooks.ts
├── schemas.ts        # only if forms exist
├── components/       # one file per presentational component
│   └── <Entity>Card.tsx
├── routes.tsx
└── index.ts
```

### 3. File contents

#### `api.ts`

Thin wrappers around `apiClient`. Each function maps to one backend endpoint. No business logic, no error UI — just the fetch and a thrown error if the response is not OK.

```typescript
import { apiClient } from '@/lib/api'
import type { components } from '@/lib/api-types'

export type <Entity> = components['schemas']['<Entity>Response']
export type <Entity>Create = components['schemas']['<Entity>Create']
export type <Entity>Update = components['schemas']['<Entity>Update']

export async function fetchAll<Entities>(): Promise<<Entity>[]> {
  const { data, error } = await apiClient.GET('/<plural>')
  if (error) throw error
  return data
}

export async function fetch<Entity>(id: string): Promise<<Entity>> {
  const { data, error } = await apiClient.GET('/<plural>/{<domain>_id}', {
    params: { path: { <domain>_id: id } },
  })
  if (error) throw error
  return data
}

export async function create<Entity>(body: <Entity>Create): Promise<<Entity>> {
  const { data, error } = await apiClient.POST('/<plural>', { body })
  if (error) throw error
  return data
}

export async function update<Entity>(id: string, body: <Entity>Update): Promise<<Entity>> {
  const { data, error } = await apiClient.PATCH('/<plural>/{<domain>_id}', {
    params: { path: { <domain>_id: id } },
    body,
  })
  if (error) throw error
  return data
}

export async function delete<Entity>(id: string): Promise<void> {
  const { error } = await apiClient.DELETE('/<plural>/{<domain>_id}', {
    params: { path: { <domain>_id: id } },
  })
  if (error) throw error
}
```

Rules:

- Import `apiClient` from `@/lib/api`. Never import `axios` or call `fetch()` directly.
- Re-export the response type and input types from this file so consumers don't import from `api-types` directly.
- Throw the error object on failure — hooks handle the error boundary.
- Only generate functions for endpoints that actually exist in `api-types.ts`.

#### `hooks.ts`

All server state flows through TanStack Query. **Never `useEffect(fetch)` directly.**

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from './api'
import type { <Entity>Create, <Entity>Update } from './api'

// ─── Cache key factory ───────────────────────────────────────────────────────
const KEYS = {
  all: ['<plural>'] as const,
  detail: (id: string) => ['<plural>', id] as const,
}

// ─── Queries ─────────────────────────────────────────────────────────────────
export function use<Entities>() {
  return useQuery({
    queryKey: KEYS.all,
    queryFn: api.fetchAll<Entities>,
  })
}

export function use<Entity>(id: string) {
  return useQuery({
    queryKey: KEYS.detail(id),
    queryFn: () => api.fetch<Entity>(id),
    enabled: !!id,
  })
}

// ─── Mutations ───────────────────────────────────────────────────────────────
export function useCreate<Entity>() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (body: <Entity>Create) => api.create<Entity>(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: KEYS.all })
    },
  })
}

export function useUpdate<Entity>() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: <Entity>Update }) =>
      api.update<Entity>(id, body),
    onSuccess: (_data, { id }) => {
      queryClient.invalidateQueries({ queryKey: KEYS.all })
      queryClient.invalidateQueries({ queryKey: KEYS.detail(id) })
    },
  })
}

export function useDelete<Entity>() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => api.delete<Entity>(id),
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: KEYS.all })
      queryClient.removeQueries({ queryKey: KEYS.detail(id) })
    },
  })
}
```

**Hook naming convention** — always follow this pattern:

| Operation | Hook name |
|-----------|-----------|
| List all | `use<Entities>()` (plural) |
| Get one | `use<Entity>(id)` (singular) |
| Create | `useCreate<Entity>()` |
| Update | `useUpdate<Entity>()` |
| Delete | `useDelete<Entity>()` |
| Domain-specific | `use<VerbEntity>()` — e.g. `useGraduatePregnancy()` |

**Cache key rules:**

- Every entity family shares one base key array: `['<plural>']`.
- Detail keys extend it: `['<plural>', id]`.
- Define keys in a `KEYS` object at the top of the file — never hardcode strings in individual hooks.
- After any mutation that changes the list (create, delete), invalidate the `KEYS.all` query.
- After any mutation that changes a single row (update), invalidate both `KEYS.all` and `KEYS.detail(id)`.
- After delete, also call `queryClient.removeQueries` on the detail key to clear the cache entry immediately.

**Optimistic updates** — use these for mutations where latency is noticeable or the UI benefit is high (e.g. toggling a boolean, reordering):

```typescript
export function useToggle<Entity>Flag() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: <Entity>Update }) =>
      api.update<Entity>(id, body),

    onMutate: async ({ id, body }) => {
      // Cancel any outgoing refetches so they don't overwrite the optimistic update.
      await queryClient.cancelQueries({ queryKey: KEYS.detail(id) })

      // Snapshot the previous value.
      const previous = queryClient.getQueryData<api.<Entity>>(KEYS.detail(id))

      // Optimistically update the cache.
      queryClient.setQueryData(KEYS.detail(id), (old: api.<Entity>) => ({
        ...old,
        ...body,
      }))

      return { previous }
    },

    onError: (_err, { id }, context) => {
      // Roll back on error.
      if (context?.previous) {
        queryClient.setQueryData(KEYS.detail(id), context.previous)
      }
    },

    onSettled: (_data, _err, { id }) => {
      // Always refetch to ensure server and client are in sync.
      queryClient.invalidateQueries({ queryKey: KEYS.detail(id) })
    },
  })
}
```

Only use optimistic updates when:

- The mutation targets a single known entity (not a list append).
- The UI reflects the result immediately (e.g. a toggle, an inline edit).
- You have the full entity in cache already.

Do not add optimistic logic to create mutations — you don't have the server-assigned `id` yet.

#### `schemas.ts`

Zod schemas for forms. One schema per form, matching the corresponding `<Entity>Create` or `<Entity>Update` type from the backend.

```typescript
import { z } from 'zod'

export const create<Entity>Schema = z.object({
  title: z.string().min(1, 'Title is required').max(128),
  // mirror Field(min_length, max_length) constraints from the Pydantic schema
})

export const update<Entity>Schema = create<Entity>Schema.partial()

export type Create<Entity>Values = z.infer<typeof create<Entity>Schema>
export type Update<Entity>Values = z.infer<typeof update<Entity>Schema>
```

Rules:

- Mirror the validation constraints from the backend's Pydantic `Field(...)` definitions. If the backend says `max_length=128`, the zod schema says `.max(128)`.
- Include a human-readable error message on every constraint that the user might trigger: `.min(1, 'Required')`, `.email('Enter a valid email')`.
- Use `.partial()` on the update schema so every field is optional — the backend accepts partial PATCH bodies.
- Export both the schema and the inferred type.
- Do not import from `api-types.ts` here — keep schemas independent of the generated types.

#### `components/`

Presentational components. Each component receives typed props; it does not fetch data itself.

```typescript
// components/<Entity>Card.tsx
import type { <Entity> } from '../api'

interface <Entity>CardProps {
  <domain>: <Entity>
  onEdit?: () => void
  onDelete?: () => void
}

export function <Entity>Card({ <domain>, onEdit, onDelete }: <Entity>CardProps) {
  return (
    <div className="rounded-lg border border-border p-4 space-y-2">
      {/* render fields */}
    </div>
  )
}
```

Rules:

- Props are typed using the re-exported type from `api.ts`, not the raw `components['schemas']` type.
- Callbacks (`onEdit`, `onDelete`) are plain functions passed from the route/page — no mutation calls inside a card.
- Use shadcn primitives from `@/components/ui/` for interactive elements (Button, Dialog, etc.). Do not style them manually — apply Tailwind to the wrapper.
- Tailwind only. No CSS modules, no inline `style={}`.

#### `routes.tsx`

Route definitions and page-level components for this feature. This is where data fetching hooks and presentational components are composed.

```typescript
import { Route } from 'react-router-dom'
import { use<Entities>, useDelete<Entity> } from './hooks'
import { <Entity>Card } from './components/<Entity>Card'

export function <Entities>Route() {
  const { data: <plural>, isLoading } = use<Entities>()
  const { mutate: delete<Entity> } = useDelete<Entity>()

  if (isLoading) return <p className="p-8 text-muted-foreground">Loading…</p>

  return (
    <div className="p-8 space-y-4">
      <h1 className="text-2xl font-semibold"><Entities></h1>
      <div className="grid gap-3">
        {<plural>?.map((<domain>) => (
          <<Entity>Card
            key={<domain>.id}
            <domain>={<domain>}
            onDelete={() => delete<Entity>(<domain>.id)}
          />
        ))}
      </div>
    </div>
  )
}

// Export route definitions for wiring into App.tsx
export const <domain>Routes = (
  <Route path="/<plural>" element={<<Entities>Route />} />
)
```

Rules:

- Page components live here, not in `src/pages/`. Keep `src/pages/` for standalone pages with no feature-folder backing.
- Loading states must be handled explicitly — always check `isLoading` before rendering data.
- Error states: if the query has an `error`, show a minimal message or re-throw to an error boundary — never silently swallow.
- Keep page components thin: one hook call per data dependency, pass everything down to presentational components.

#### `index.ts`

Public surface of the feature. Only export what other parts of the app need to import.

```typescript
export { <domain>Routes } from './routes'
export type { <Entity> } from './api'
// Export hooks only if another feature actually needs them cross-feature.
// Prefer co-locating hook usage in routes.tsx.
```

Rules:

- Do not re-export everything blindly with `export * from`. Be explicit.
- Only export what is genuinely needed outside this feature folder.
- Types that are only used internally (form values, intermediate shapes) stay unexported.

### 4. Wire the route into App.tsx

Open `frontend/src/App.tsx` and add the new routes inside the `<Routes>` block:

```typescript
import { <domain>Routes } from '@/features/<domain>'

// inside <Routes>:
{<domain>Routes}
```

If the route should be behind auth (almost always yes), wrap it in a protected route component. If no protected route wrapper exists yet, create a simple one:

```typescript
// src/components/ProtectedRoute.tsx
import { Navigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'

function useMe() {
  return useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/auth/me')
      if (error) throw error
      return data
    },
    retry: false,
  })
}

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { data, isLoading } = useMe()
  if (isLoading) return null
  if (!data) return <Navigate to="/login" replace />
  return <>{children}</>
}
```

### 5. Verify

Before declaring done:

```bash
cd frontend
pnpm build        # zero TypeScript errors
pnpm lint         # zero ESLint errors
```

If `pnpm build` fails on a type error from `api-types.ts`, the schema likely changed — re-run `pnpm gen:api` and check whether the generated path or property name differs from what you wrote.

## Output to the user

After scaffolding, summarize:

1. The list of files created (paths only, no contents — they can read them).
2. The hooks generated and their signatures (e.g. `useMembers()`, `useCreateMember()`).
3. The routes added to `App.tsx`.
4. Any decisions you made that the user didn't specify (e.g. "I built a card component for the list and a modal for create — adjust in `components/` if you want a separate page instead.").
5. Suggested next step (usually: "Start the dev server with `pnpm dev` and verify the golden path.").

## Common mistakes to avoid

- Hand-writing TypeScript types that duplicate Pydantic schemas. Always import from `api-types.ts` via `api.ts`.
- Calling `useQueryClient` at module scope. It must be called inside a React component or hook.
- Hardcoding cache key strings in multiple places instead of using the `KEYS` factory.
- Forgetting to invalidate `KEYS.all` after a create or delete — the list will show stale data.
- Adding `onMutate` to a create mutation — you cannot optimistically add an item without a server-assigned `id`.
- Importing from `@/components/ui/` files and modifying them. Those are shadcn primitives — wrap them, don't edit them.
- Putting fetch logic in a presentational component. Fetching belongs in `routes.tsx` (via hooks); components receive data as props.
- Forgetting `enabled: !!id` on a detail query — it will fire immediately with `undefined` and produce a 422 from the backend.
- Using `data?.items` when the backend returns a plain array. Always check `api-types.ts` for the actual response shape before assuming pagination.
