import { NextResponse } from "next/server"
import { z } from "zod"
import { publicApi, ApiError } from "@/lib/api-client"

/**
 * Public marketing lead-form endpoint. Validates input with Zod, forwards to
 * FastAPI. No auth — FastAPI's /api/v1/public/leads scopes by org slug.
 */

const leadSchema = z.object({
  email: z.string().email(),
  firstName: z.string().min(1).max(100).optional(),
  lastName: z.string().min(1).max(100).optional(),
  company: z.string().max(200).optional(),
  phone: z.string().max(50).optional(),
  message: z.string().max(2000).optional(),
  source: z.string().max(50).default("marketing-site")
})

export async function POST(req: Request) {
  const json = await req.json().catch(() => null)
  const parsed = leadSchema.safeParse(json)
  if (!parsed.success) {
    return NextResponse.json(
      { error: "Invalid input", issues: parsed.error.issues },
      { status: 400 }
    )
  }

  try {
    const result = await publicApi("/api/v1/public/leads", {
      method: "POST",
      body: parsed.data
    })
    return NextResponse.json(result, { status: 201 })
  } catch (err) {
    if (err instanceof ApiError) {
      return NextResponse.json({ error: "Upstream error", body: err.body }, { status: err.status })
    }
    return NextResponse.json({ error: "Internal error" }, { status: 500 })
  }
}
