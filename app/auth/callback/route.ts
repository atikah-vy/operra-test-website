import { NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/dashboard'

  if (code) {
    const supabase = await createClient()
    const { data, error } = await supabase.auth.exchangeCodeForSession(code)

    if (!error && data.user) {
      // Upsert profile for OAuth users (Google sign-in)
      await supabase.from('profiles').upsert({
        id: data.user.id,
        full_name: data.user.user_metadata?.full_name ?? data.user.user_metadata?.name ?? null,
        email: data.user.email ?? null,
        company: data.user.user_metadata?.company ?? null,
        phone: data.user.user_metadata?.phone ?? null,
      })

      return NextResponse.redirect(`${origin}${next}`)
    }
  }

  return NextResponse.redirect(`${origin}/login?error=auth_callback_failed`)
}
