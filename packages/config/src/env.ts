import { z } from "zod"

/**
 * Validated env for the web app. Server vars are kept out of client bundles by
 * Next.js as long as they don't start with NEXT_PUBLIC_.
 *
 * Uses a Proxy so we throw a descriptive error on first access, rather than
 * crashing the whole process at import time (helpful during `next build`).
 */
const serverSchema = z.object({
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
  CLERK_SECRET_KEY: z.string().min(1),
  CLERK_WEBHOOK_SIGNING_SECRET: z.string().optional(),
  API_BASE_URL: z.string().url().default("http://localhost:8000")
})

const clientSchema = z.object({
  NEXT_PUBLIC_APP_URL: z.string().url().default("http://localhost:3000"),
  NEXT_PUBLIC_API_BASE_URL: z.string().url().default("http://localhost:8000"),
  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: z.string().min(1),
  NEXT_PUBLIC_CLERK_SIGN_IN_URL: z.string().default("/sign-in"),
  NEXT_PUBLIC_CLERK_SIGN_UP_URL: z.string().default("/sign-up")
})

type ServerEnv = z.infer<typeof serverSchema>
type ClientEnv = z.infer<typeof clientSchema>

function createLazyEnv<T extends z.ZodTypeAny>(
  schema: T,
  raw: Record<string, string | undefined>,
  label: string
): z.infer<T> {
  let cached: z.infer<T> | null = null
  return new Proxy({} as z.infer<T>, {
    get(_t, prop: string) {
      if (!cached) {
        const parsed = schema.safeParse(raw)
        if (!parsed.success) {
          throw new Error(
            `Invalid ${label} env vars:\n${parsed.error.issues
              .map((i) => `  - ${i.path.join(".")}: ${i.message}`)
              .join("\n")}`
          )
        }
        cached = parsed.data
      }
      return cached[prop as keyof typeof cached]
    }
  })
}

const isServer = typeof window === "undefined"

export const env: ServerEnv & ClientEnv = new Proxy({} as ServerEnv & ClientEnv, {
  get(_t, prop: string) {
    const client = createLazyEnv(
      clientSchema,
      {
        NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
        NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
        NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY,
        NEXT_PUBLIC_CLERK_SIGN_IN_URL: process.env.NEXT_PUBLIC_CLERK_SIGN_IN_URL,
        NEXT_PUBLIC_CLERK_SIGN_UP_URL: process.env.NEXT_PUBLIC_CLERK_SIGN_UP_URL
      },
      "client"
    )
    if (prop.startsWith("NEXT_PUBLIC_")) return (client as any)[prop]
    if (!isServer) {
      throw new Error(`Attempted to read server env "${prop}" from the browser.`)
    }
    const server = createLazyEnv(
      serverSchema,
      {
        NODE_ENV: process.env.NODE_ENV,
        CLERK_SECRET_KEY: process.env.CLERK_SECRET_KEY,
        CLERK_WEBHOOK_SIGNING_SECRET: process.env.CLERK_WEBHOOK_SIGNING_SECRET,
        API_BASE_URL: process.env.API_BASE_URL
      },
      "server"
    )
    return (server as any)[prop]
  }
})
