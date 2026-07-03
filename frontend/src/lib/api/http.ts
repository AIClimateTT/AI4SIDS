/** Authenticated JSON transport for the AI4SIDS API.
 *
 * The legacy `client.ts` serves the unauthenticated public dashboard;
 * authenticated resources (orgs, uploads, …) go through this helper.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL ?? ''
const TOKEN_KEY = 'ai4sids_token'

export class HttpError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message)
    this.name = 'HttpError'
  }
}

interface FastApiValidationItem {
  loc?: Array<string | number>
  msg?: string
}

export async function http<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem(TOKEN_KEY)
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(init.headers as Record<string, string> | undefined),
  }
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(`${API_BASE_URL}${path}`, { ...init, headers })

  if (!res.ok) {
    const data = await res.json().catch(() => null)
    let message = `Request failed with status ${res.status}`
    const detail = data?.detail
    if (typeof detail === 'string') {
      message = detail
    } else if (Array.isArray(detail)) {
      message = detail
        .map((e: FastApiValidationItem) => `${e.loc?.join('.')}: ${e.msg}`)
        .join(', ')
    }
    throw new HttpError(message, res.status)
  }

  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}
