import { auth } from "@clerk/nextjs/server"

/**
 * Server-side typed fetch helper for talking to the FastAPI backend.
 * Always forwards the current Clerk session JWT as Bearer.
 *
 * Client components should not call this directly — use server components,
 * server actions, or route handlers that delegate here.
 */

const DEFAULT_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000"

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly body: unknown,
    message?: string
  ) {
    super(message ?? `API request failed: ${status}`)
    this.name = "ApiError"
  }
}

interface ApiOptions extends Omit<RequestInit, "body"> {
  body?: unknown
  /** Skip auth (e.g. for the public lead form). */
  anonymous?: boolean
  /** Next.js cache tag. */
  revalidate?: number | false
  tags?: string[]
}

export async function api<T = unknown>(path: string, opts: ApiOptions = {}): Promise<T> {
  const { anonymous, body, headers, revalidate, tags, ...rest } = opts

  const finalHeaders: Record<string, string> = {
    accept: "application/json",
    ...(headers as Record<string, string> | undefined)
  }

  if (body !== undefined) finalHeaders["content-type"] = "application/json"

  if (!anonymous) {
    const { getToken, orgId } = await auth()
    const token = await getToken({ template: "operra-api" }).catch(() => getToken())
    if (token) finalHeaders.authorization = `Bearer ${token}`
    if (orgId) finalHeaders["x-org-id"] = orgId
  }

  const url = path.startsWith("http") ? path : `${DEFAULT_BASE_URL}${path}`

  const res = await fetch(url, {
    ...rest,
    headers: finalHeaders,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    next:
      revalidate === false
        ? { revalidate: 0, tags }
        : revalidate !== undefined
          ? { revalidate, tags }
          : tags
            ? { tags }
            : undefined
  })

  const ct = res.headers.get("content-type") ?? ""
  const payload: unknown = ct.includes("application/json")
    ? await res.json().catch(() => null)
    : await res.text().catch(() => null)

  if (!res.ok) throw new ApiError(res.status, payload)
  return payload as T
}

/** Public (unauthenticated) variant for marketing endpoints. */
export async function publicApi<T = unknown>(path: string, opts: Omit<ApiOptions, "anonymous"> = {}): Promise<T> {
  return api<T>(path, { ...opts, anonymous: true })
}
