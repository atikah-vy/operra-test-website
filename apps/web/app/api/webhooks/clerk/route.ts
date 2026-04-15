import { headers } from "next/headers"
import { Webhook } from "svix"

/**
 * Clerk webhook → forwards verified payload to FastAPI so the backend keeps
 * users/organizations rows in sync (multi-tenancy source of truth).
 *
 * Configure the endpoint URL in Clerk Dashboard → Webhooks → Add endpoint:
 *   {NEXT_PUBLIC_APP_URL}/api/webhooks/clerk
 * Events to subscribe: user.created, user.updated, user.deleted,
 * organization.created, organization.updated, organization.deleted,
 * organizationMembership.created, organizationMembership.updated,
 * organizationMembership.deleted.
 */
export async function POST(req: Request) {
  const secret = process.env.CLERK_WEBHOOK_SIGNING_SECRET
  if (!secret) {
    return new Response("Missing CLERK_WEBHOOK_SIGNING_SECRET", { status: 500 })
  }

  const h = await headers()
  const svixId = h.get("svix-id")
  const svixTimestamp = h.get("svix-timestamp")
  const svixSig = h.get("svix-signature")
  if (!svixId || !svixTimestamp || !svixSig) {
    return new Response("Missing Svix headers", { status: 400 })
  }

  const body = await req.text()
  let evt: unknown
  try {
    evt = new Webhook(secret).verify(body, {
      "svix-id": svixId,
      "svix-timestamp": svixTimestamp,
      "svix-signature": svixSig
    })
  } catch {
    return new Response("Invalid signature", { status: 401 })
  }

  // Forward to FastAPI. The backend is the source of truth for org/user rows.
  const apiBase = process.env.API_BASE_URL ?? "http://localhost:8000"
  const res = await fetch(`${apiBase}/api/v1/webhooks/clerk`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-forwarded-clerk": "verified"
    },
    body: JSON.stringify(evt)
  })

  if (!res.ok) {
    const text = await res.text().catch(() => "")
    return new Response(`Backend sync failed: ${text}`, { status: 502 })
  }

  return Response.json({ received: true })
}
