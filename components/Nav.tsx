'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
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
            <li><a href="/#features">Platform</a></li>
            <li><a href="/#modules">Modules</a></li>
            <li><a href="/#how-it-works">How It Works</a></li>
            <li><a href="/#compare">Compare</a></li>
            <li><a href="/#docs">Docs</a></li>
          </ul>

          <div className={styles.navCta}>
            <Link href="/login" className="btn btn-ghost">Sign in</Link>
            <Link href="/signup" className="btn btn-primary">Get Started</Link>
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
        <a href="/#features" className={styles.mobileLink} onClick={close}>Platform</a>
        <a href="/#modules" className={styles.mobileLink} onClick={close}>Modules</a>
        <a href="/#how-it-works" className={styles.mobileLink} onClick={close}>How It Works</a>
        <a href="/#compare" className={styles.mobileLink} onClick={close}>Compare</a>
        <a href="/#docs" className={styles.mobileLink} onClick={close}>Docs</a>
        <div className={styles.mobileDivider} />
        <Link href="/login" className="btn btn-ghost" onClick={close}>Sign in</Link>
        <Link href="/signup" className="btn btn-primary" onClick={close}>Get Started →</Link>
      </div>
    </>
  )
}
