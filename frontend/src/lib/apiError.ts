interface ApiErrorBody {
  code?: string
  detail?: string
  errors?: { field: string; message: string }[]
}

export function getErrorMessage(error: unknown): string {
  if (error !== null && typeof error === 'object') {
    const body = error as ApiErrorBody
    if (typeof body.detail === 'string' && body.detail) return body.detail
  }
  return 'Something went wrong. Please try again.'
}
