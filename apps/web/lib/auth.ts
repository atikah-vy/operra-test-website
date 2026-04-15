import { auth, currentUser } from "@clerk/nextjs/server"
import { redirect } from "next/navigation"

export async function requireAuth() {
  const session = await auth()
  if (!session.userId) redirect("/sign-in")
  return session
}

export async function getActiveOrgId() {
  const session = await auth()
  return session.orgId ?? null
}

export async function getCurrentUserSafe() {
  try {
    return await currentUser()
  } catch {
    return null
  }
}
