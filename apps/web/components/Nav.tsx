'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { SignedIn, SignedOut, UserButton } from '@clerk/nextjs'
import styles from './Nav.module.css'

export default function Nav() {
  const [open, setOpen] = useState(false)

  const close = () => {
    setOpen(false)
    document.body.style.overflow = ''
  }

  const toggle = () => {
    const next = !open
    setOpen(next)
    document.body.style.overflow = next ? 'hidden' : ''
  }

  return (
    <>
      <nav className={styles.nav}>
        <div className={styles.navInner}>
          <Link href="/" className={styles.navLogo}>
            <Image
              src="/brand_logo_page/Brand LOGO.jpg"
              alt="Operra logo"
              width={32}
              height={32}
              style={{ height: 32, width: 'auto', objectFit: 'contain' }}
            />
          </Link>

          <ul className={styles.navLinks}>
            <li><Link href="/#features">Platform</Link></li>
            <li><Link href="/#modules">Modules</Link></li>
            <li><Link href="/#how-it-works">How It Works</Link></li>
            <li><Link href="/#compare">Compare</Link></li>
            <li><Link href="/dashboard">Dashboard</Link></li>
          </ul>

          <div className={styles.navCta}>
            <SignedOut>
              <Link href="/sign-in" className="btn btn-ghost">Sign in</Link>
              <Link href="/sign-up" className="btn btn-primary">Get Started</Link>
            </SignedOut>
            <SignedIn>
              <Link href="/dashboard" className="btn btn-ghost">Dashboard</Link>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
          </div>

          <button
            className={`${styles.hamburger} ${open ? styles.open : ''}`}
            onClick={toggle}
            aria-label="Open menu"
            aria-expanded={open}
          >
            <span />
            <span />
            <span />
          </button>
        </div>
      </nav>

      <div className={`${styles.mobileMenu} ${open ? styles.mobileMenuOpen : ''}`}>
        <Link href="/#features" className={styles.mobileLink} onClick={close}>Platform</Link>
        <Link href="/#modules" className={styles.mobileLink} onClick={close}>Modules</Link>
        <Link href="/#how-it-works" className={styles.mobileLink} onClick={close}>How It Works</Link>
        <Link href="/#compare" className={styles.mobileLink} onClick={close}>Compare</Link>
        <Link href="/dashboard" className={styles.mobileLink} onClick={close}>Dashboard</Link>
        <div className={styles.mobileDivider} />
        <SignedOut>
          <Link href="/sign-in" className="btn btn-ghost" onClick={close}>Sign in</Link>
          <Link href="/sign-up" className="btn btn-primary" onClick={close}>Get Started →</Link>
        </SignedOut>
        <SignedIn>
          <Link href="/dashboard" className="btn btn-primary" onClick={close}>Go to Dashboard →</Link>
        </SignedIn>
      </div>
    </>
  )
}
