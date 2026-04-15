'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import styles from '../auth.module.css'

export default function LoginForm() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    const supabase = createClient()
    const { error } = await supabase.auth.signInWithPassword({ email, password })

    if (error) {
      setError(error.message)
      setLoading(false)
    } else {
      router.push('/dashboard')
      router.refresh()
    }
  }

  const handleGoogleLogin = async () => {
    const supabase = createClient()
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: `${window.location.origin}/auth/callback` },
    })
  }

  return (
    <div className={styles.authSplit}>

      {/* ── LEFT PANEL ── */}
      <div className={styles.authLeft}>
        <div className={styles.authLeftDecor1} />
        <div className={styles.authLeftDecor2} />
        <div className={styles.authLeftDecor3} />

        <div className={styles.authLeftTop}>
          <Image
            src="/brand_logo_page/Brand LOGO.jpg"
            alt="Operra"
            width={38}
            height={38}
            style={{ height: 38, width: 'auto', objectFit: 'contain', borderRadius: 8 }}
          />
          <span className={styles.authLeftBrand}>Operra</span>
        </div>

        <div className={styles.authLeftContent}>
          <div className={styles.authLeftBadge}>
            <span className={styles.authLeftBadgeDot} />
            Now in Public Beta
          </div>

          <h1 className={styles.authLeftHeading}>
            Welcome!<br />
            <span>Build, manage,</span><br />
            and grow.
          </h1>

          <p className={styles.authLeftSub}>
            One intelligent platform for CRM, tasks, invoicing, and analytics.
            Everything your team needs, from day one.
          </p>

          <div className={styles.authFeatures}>
            {[
              { icon: '📊', text: 'Real-time dashboard & analytics' },
              { icon: '👥', text: 'CRM & customer pipeline' },
              { icon: '✅', text: 'Tasks, projects & collaboration' },
              { icon: '🧾', text: 'Invoicing & payment tracking' },
            ].map((f) => (
              <div className={styles.authFeatureItem} key={f.text}>
                <div className={styles.authFeatureIcon}>{f.icon}</div>
                <span className={styles.authFeatureText}>{f.text}</span>
              </div>
            ))}
          </div>

          <div className={styles.authStats}>
            <div className={styles.authStat}>
              <div className={styles.authStatValue}>8,400+</div>
              <div className={styles.authStatLabel}>Teams</div>
            </div>
            <div className={styles.authStatDivider} />
            <div className={styles.authStat}>
              <div className={styles.authStatValue}>99.9%</div>
              <div className={styles.authStatLabel}>Uptime</div>
            </div>
            <div className={styles.authStatDivider} />
            <div className={styles.authStat}>
              <div className={styles.authStatValue}>$0</div>
              <div className={styles.authStatLabel}>To Start</div>
            </div>
          </div>
        </div>

        <div className={styles.authLeftFooter}>
          <Link href="/" className={styles.authBackLink}>
            ← Back to home
          </Link>
          <span>© 2025 Operra</span>
        </div>
      </div>

      {/* ── RIGHT PANEL ── */}
      <div className={styles.authRight}>
        <div className={styles.authCard}>

          <div className={styles.authCardHeader}>
            <h2 className={styles.authCardTitle}>Sign In</h2>
            <p className={styles.authCardSub}>Welcome back! Enter your details to continue.</p>
          </div>

          <div className={styles.authTabs}>
            <Link href="/login" className={`${styles.authTab} ${styles.authTabActive}`}>Sign in</Link>
            <Link href="/signup" className={styles.authTab}>Create account</Link>
          </div>

          <form onSubmit={handleEmailLogin} className={styles.form}>
            <div className={styles.formGroup}>
              <label htmlFor="email">Email address</label>
              <input
                id="email"
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>

            <div className={styles.formGroup}>
              <div className={styles.formLabelRow}>
                <label htmlFor="password">Password</label>
                <a href="#" className={styles.forgotLink}>Forgot password?</a>
              </div>
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
              />
            </div>

            {error && <p className={styles.errorMsg}>{error}</p>}

            <button type="submit" className={styles.btnSubmit} disabled={loading}>
              {loading ? 'Signing in…' : <>Sign in <ArrowRight /></>}
            </button>
          </form>

          <div className={styles.divider}>or</div>

          <button type="button" className={styles.btnGoogle} onClick={handleGoogleLogin}>
            <GoogleIcon />
            Sign in with Google
          </button>

          <p className={styles.authFooterText}>
            Don&apos;t have an account?{' '}
            <Link href="/signup">Sign up free</Link>
          </p>
        </div>
      </div>

    </div>
  )
}

function ArrowRight() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M17.64 9.205c0-.639-.057-1.252-.164-1.841H9v3.481h4.844a4.14 4.14 0 01-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/>
      <path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z" fill="#34A853"/>
      <path d="M3.964 10.71A5.41 5.41 0 013.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 000 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>
      <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z" fill="#EA4335"/>
    </svg>
  )
}
