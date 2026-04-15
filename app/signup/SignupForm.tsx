'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import styles from '../auth.module.css'

export default function SignupForm() {
  const router = useRouter()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [company, setCompany] = useState('')
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const passwordMismatch = confirmPassword.length > 0 && password !== confirmPassword

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault()
    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }
    setLoading(true)
    setError(null)

    const supabase = createClient()
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
          company,
          phone,
        },
      },
    })

    if (error) {
      setError(error.message)
      setLoading(false)
      return
    }

    if (data.user) {
      await supabase.from('profiles').upsert({
        id: data.user.id,
        full_name: fullName,
        email,
        company: company || null,
        phone: phone || null,
      })
    }

    setSuccess(true)
    setLoading(false)
    setTimeout(() => router.push('/dashboard'), 1500)
  }

  const handleGoogleSignup = async () => {
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
            width={40}
            height={40}
            style={{ height: 40, width: 'auto', objectFit: 'contain', borderRadius: 8 }}
          />
          <span className={styles.authLeftBrand}>Operra</span>
        </div>

        <div className={styles.authLeftContent}>
          <div className={styles.authLeftBadge}>
            <span className={styles.authLeftBadgeDot} />
            Free — No credit card needed
          </div>

          <h1 className={styles.authLeftHeading}>
            Welcome!<br />
            <span>Start building</span><br />
            for free.
          </h1>

          <p className={styles.authLeftSub}>
            Get your entire business running in one platform.
            Start free and be operational in under a day.
          </p>

          <div className={styles.authFeatures}>
            {[
              { icon: '🚀', text: 'Up and running in under a day' },
              { icon: '🔒', text: 'Enterprise-grade security & privacy' },
              { icon: '🔗', text: 'Connects to tools you already use' },
              { icon: '💬', text: 'Dedicated onboarding support' },
            ].map((f) => (
              <div className={styles.authFeatureItem} key={f.text}>
                <div className={styles.authFeatureIcon}>{f.icon}</div>
                <span className={styles.authFeatureText}>{f.text}</span>
              </div>
            ))}
          </div>

          <div className={styles.authStats}>
            <div className={styles.authStat}>
              <div className={styles.authStatValue}>$0</div>
              <div className={styles.authStatLabel}>To Start</div>
            </div>
            <div className={styles.authStatDivider} />
            <div className={styles.authStat}>
              <div className={styles.authStatValue}>4h</div>
              <div className={styles.authStatLabel}>To Launch</div>
            </div>
            <div className={styles.authStatDivider} />
            <div className={styles.authStat}>
              <div className={styles.authStatValue}>40%</div>
              <div className={styles.authStatLabel}>Less Admin</div>
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
            <h2 className={styles.authCardTitle}>Create account</h2>
            <p className={styles.authCardSub}>Start for free — no credit card required.</p>
          </div>

          <div className={styles.authTabs}>
            <Link href="/login" className={styles.authTab}>Sign in</Link>
            <Link href="/signup" className={`${styles.authTab} ${styles.authTabActive}`}>Create account</Link>
          </div>

          {success ? (
            <div className={styles.successMsg}>
              <span>🎉</span>
              <p>Account created! Redirecting to your dashboard…</p>
            </div>
          ) : (
            <form onSubmit={handleSignup} className={styles.form}>
              <div className={styles.formGroup}>
                <label htmlFor="fullName">Full name</label>
                <input
                  id="fullName"
                  type="text"
                  placeholder="Jane Smith"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                  autoComplete="name"
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="email">Work email</label>
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
                <label htmlFor="company">
                  Company name <span className={styles.optional}>optional</span>
                </label>
                <input
                  id="company"
                  type="text"
                  placeholder="Acme Inc."
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  autoComplete="organization"
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="phone">
                  Phone number <span className={styles.optional}>optional</span>
                </label>
                <input
                  id="phone"
                  type="tel"
                  placeholder="+1 555 000 0000"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  autoComplete="tel"
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="password">Password</label>
                <input
                  id="password"
                  type="password"
                  placeholder="Min. 8 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={8}
                  autoComplete="new-password"
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="confirmPassword">Confirm password</label>
                <input
                  id="confirmPassword"
                  type="password"
                  placeholder="Re-enter your password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  autoComplete="new-password"
                />
                {passwordMismatch && (
                  <p className={styles.hintMsg}>Passwords do not match</p>
                )}
              </div>

              {error && <p className={styles.errorMsg}>{error}</p>}

              <button
                type="submit"
                className={styles.btnSubmit}
                disabled={loading || passwordMismatch}
              >
                {loading ? 'Creating account…' : 'Create free account'}
              </button>
            </form>
          )}

          <div className={styles.divider}>or</div>

          <button type="button" className={styles.btnGoogle} onClick={handleGoogleSignup}>
            <GoogleIcon />
            Sign up with Google
          </button>

          <p className={styles.authFooterText}>
            Already have an account?{' '}
            <Link href="/login">Sign in</Link>
          </p>
        </div>
      </div>

    </div>
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
