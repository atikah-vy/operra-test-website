'use client'

import { useRouter } from 'next/navigation'
import Image from 'next/image'
import type { User } from '@supabase/supabase-js'
import { createClient } from '@/lib/supabase/client'
import styles from './dashboard.module.css'

interface Profile {
  full_name: string | null
  email: string | null
  company: string | null
  phone: string | null
}

interface Props {
  user: User
  profile: Profile | null
}

export default function DashboardClient({ user, profile }: Props) {
  const router = useRouter()

  const displayName =
    profile?.full_name ||
    user.user_metadata?.full_name ||
    user.email?.split('@')[0] ||
    'there'

  const companyName =
    profile?.company ||
    user.user_metadata?.company ||
    null

  const handleSignOut = async () => {
    const supabase = createClient()
    await supabase.auth.signOut()
    router.push('/')
    router.refresh()
  }

  return (
    <div className={styles.page}>
      {/* ── TOP NAV ── */}
      <nav className={styles.nav}>
        <div className={styles.navInner}>
          <div className={styles.navLogo}>
            <Image
              src="/brand_logo_page/Brand LOGO.jpg"
              alt="Operra"
              width={28}
              height={28}
              style={{ height: 28, width: 'auto', objectFit: 'contain' }}
            />
            <span className={styles.navLogoText}>Operra</span>
          </div>
          <div className={styles.navRight}>
            <span className={styles.userEmail}>{user.email}</span>
            <button onClick={handleSignOut} className={styles.signOutBtn}>
              Sign out
            </button>
          </div>
        </div>
      </nav>

      {/* ── MAIN CONTENT ── */}
      <main className={styles.main}>
        <div className={styles.container}>

          {/* Welcome */}
          <div className={styles.welcome}>
            <h1 className={styles.welcomeTitle}>
              Welcome back, <span>{displayName}</span> 👋
            </h1>
            <p className={styles.welcomeSub}>
              {companyName ? (
                <>{companyName} &mdash; here&apos;s what&apos;s happening across your business today.</>
              ) : (
                <>Here&apos;s what&apos;s happening across your business today.</>
              )}
            </p>
          </div>

          {/* Stats */}
          <div className={styles.statsGrid}>
            {[
              { label: 'Active Deals', value: '24', delta: '+3 this week', positive: true, icon: '📈' },
              { label: 'Open Tasks', value: '57', delta: '12 due today', positive: false, icon: '✅' },
              { label: 'Invoices Sent', value: '$18,400', delta: '+$2,200 this month', positive: true, icon: '🧾' },
              { label: 'Team Members', value: '8', delta: '1 invite pending', positive: null, icon: '👥' },
            ].map((s) => (
              <div key={s.label} className={styles.statCard}>
                <div className={styles.statIcon}>{s.icon}</div>
                <div className={styles.statBody}>
                  <div className={styles.statValue}>{s.value}</div>
                  <div className={styles.statLabel}>{s.label}</div>
                  <div className={`${styles.statDelta} ${s.positive === true ? styles.positive : s.positive === false ? styles.negative : styles.neutral}`}>
                    {s.delta}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Module cards */}
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>Your modules</h2>
            <p className={styles.sectionDesc}>Jump straight into any part of Operra.</p>
          </div>

          <div className={styles.moduleGrid}>
            {[
              { icon: '👥', name: 'CRM', desc: 'Contacts, pipelines & deal history', href: '#', badge: 'Live', badgeCls: 'live' },
              { icon: '✅', name: 'Tasks', desc: 'Kanban boards & team workload', href: '#', badge: 'Live', badgeCls: 'live' },
              { icon: '🧾', name: 'Invoicing', desc: 'Create, send & track invoices', href: '#', badge: 'Live', badgeCls: 'live' },
              { icon: '📊', name: 'Analytics', desc: 'KPIs, revenue trends & metrics', href: '#', badge: 'Live', badgeCls: 'live' },
              { icon: '🔔', name: 'Inbox', desc: 'Priority-filtered notifications', href: '#', badge: 'Beta', badgeCls: 'beta' },
              { icon: '📄', name: 'Docs', desc: 'Documents linked to deals & tasks', href: '#', badge: 'Beta', badgeCls: 'beta' },
            ].map((m) => (
              <a key={m.name} href={m.href} className={styles.moduleCard}>
                <div className={styles.moduleIcon}>{m.icon}</div>
                <div className={styles.moduleBody}>
                  <div className={styles.moduleName}>{m.name}</div>
                  <div className={styles.moduleDesc}>{m.desc}</div>
                </div>
                <span className={`${styles.moduleBadge} ${styles[m.badgeCls]}`}>{m.badge}</span>
              </a>
            ))}
          </div>

          {/* Quick actions */}
          <div className={styles.actionsRow}>
            <div className={styles.actionCard}>
              <h3>Invite your team</h3>
              <p>Add teammates with role-based access. Everyone sees what they need.</p>
              <button className={styles.actionBtn}>Invite members →</button>
            </div>
            <div className={styles.actionCard}>
              <h3>Import your data</h3>
              <p>Bring in contacts and deals from spreadsheets or your previous CRM.</p>
              <button className={styles.actionBtn}>Start import →</button>
            </div>
            <div className={styles.actionCard}>
              <h3>Create your first invoice</h3>
              <p>Generate a professional invoice from a deal in under a minute.</p>
              <button className={styles.actionBtn}>New invoice →</button>
            </div>
          </div>

        </div>
      </main>
    </div>
  )
}
