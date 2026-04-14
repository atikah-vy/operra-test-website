import Link from 'next/link'
import Nav from '@/components/Nav'
import Footer from '@/components/Footer'

export default function HomePage() {
  return (
    <>
      <Nav />
      <main>

        {/* ── HERO ── */}
        <section className="hero">
          <div className="container">
            <div className="hero-badge">
              <span className="hero-badge-dot" />
              Now in Public Beta
            </div>
            <h1>
              One System.<br />
              <span className="accent">Total Control.</span>
            </h1>
            <p className="hero-sub">
              Operra brings your entire business operation into one intelligent platform —
              CRM, tasks, invoicing, and analytics, unified from day one.
            </p>
            <div className="hero-actions">
              <Link href="/signup" className="btn btn-primary btn-lg">Start Free Today →</Link>
              <a href="#how-it-works" className="btn btn-ghost btn-lg">Book a Demo</a>
            </div>

            {/* Stats Bar */}
            <div className="stats-bar">
              <div className="stat-item">
                <div className="stat-value blue">8,400+</div>
                <div className="stat-label">Teams Using Operra</div>
              </div>
              <div className="stat-divider" />
              <div className="stat-item">
                <div className="stat-value blue">2.1M</div>
                <div className="stat-label">Tasks Managed / Month</div>
              </div>
              <div className="stat-divider" />
              <div className="stat-item">
                <div className="stat-value blue">99.9%</div>
                <div className="stat-label">Uptime SLA</div>
              </div>
              <div className="stat-divider" />
              <div className="stat-item">
                <div className="stat-value blue">40%</div>
                <div className="stat-label">Less Admin Overhead</div>
              </div>
              <div className="stat-divider" />
              <div className="stat-item">
                <div className="stat-value blue">$0</div>
                <div className="stat-label">To Start</div>
              </div>
            </div>
          </div>
        </section>

        {/* ── FEATURES ── */}
        <section className="features-section" id="features">
          <div className="container">
            <div className="features-header">
              <div className="section-label">Platform</div>
              <h2 className="section-title">Everything your team needs, built in</h2>
              <p className="section-desc">
                No more stitching together eight tools. Operra is a single, coherent system
                designed to work the way your business actually works.
              </p>
            </div>

            <div className="features-grid">
              {[
                {
                  icon: '📊',
                  title: 'Real-Time Dashboard',
                  desc: 'A live command centre for your entire operation. Track revenue, pipeline, team performance, and task completion in one view — no manual reports.',
                  tags: [
                    { label: 'Analytics', cls: 'tag-blue' },
                    { label: 'Live Data', cls: 'tag-blue' },
                    { label: 'Customisable', cls: '' },
                  ],
                },
                {
                  icon: '👥',
                  title: 'CRM & Customer Management',
                  desc: 'Manage contacts, track deal stages, log interactions, and never let a follow-up slip. Built for teams that close deals and keep clients happy.',
                  tags: [
                    { label: 'Pipeline', cls: 'tag-blue' },
                    { label: 'Contacts', cls: 'tag-blue' },
                    { label: 'Deal Tracking', cls: '' },
                  ],
                },
                {
                  icon: '✅',
                  title: 'Tasks & Project Management',
                  desc: 'Assign, prioritise, and track work across every team. Linked directly to clients and deals so nothing gets lost between departments.',
                  tags: [
                    { label: 'Productivity', cls: 'tag-green' },
                    { label: 'Boards', cls: 'tag-blue' },
                    { label: 'Deadlines', cls: '' },
                  ],
                },
                {
                  icon: '🧾',
                  title: 'Invoicing & Finance',
                  desc: 'Generate invoices from completed work in seconds. Track outstanding payments, automate reminders, and connect to your accounting tools.',
                  tags: [
                    { label: 'Finance', cls: 'tag-amber' },
                    { label: 'Billing', cls: 'tag-blue' },
                    { label: 'Payments', cls: '' },
                  ],
                },
                {
                  icon: '🔔',
                  title: 'Smart Notifications',
                  desc: 'Stay informed without the noise. Operra surfaces what actually needs your attention — overdue tasks, unpaid invoices, stalled deals — nothing else.',
                  tags: [
                    { label: 'Alerts', cls: 'tag-blue' },
                    { label: 'Digest Mode', cls: '' },
                    { label: 'Priority Inbox', cls: '' },
                  ],
                },
                {
                  icon: '🔍',
                  title: 'Universal Search',
                  desc: 'Find any client, task, invoice, or note in under a second. Search works across every module in Operra — one place, one query, instant results.',
                  tags: [
                    { label: 'Instant', cls: 'tag-blue' },
                    { label: 'Cross-Module', cls: '' },
                    { label: 'Filters', cls: '' },
                  ],
                },
              ].map((f) => (
                <div className="feature-card" key={f.title}>
                  <div className="feature-icon">{f.icon}</div>
                  <div className="feature-title">{f.title}</div>
                  <p className="feature-desc">{f.desc}</p>
                  <div className="feature-tags">
                    {f.tags.map((t) => (
                      <span key={t.label} className={`tag ${t.cls}`}>{t.label}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── MODULES ── */}
        <section className="products-section" id="modules">
          <div className="container">
            <div className="section-label">Modules</div>
            <h2 className="section-title">Built for every part of your business</h2>
            <p className="section-desc" style={{ marginBottom: '3rem' }}>
              Each Operra module is production-ready on its own — together, they form
              a complete operating system for your company.
            </p>

            <div className="products-grid">
              {[
                { name: 'Operra CRM', desc: 'Full-cycle customer relationship management — contacts, pipelines, and deal history.', badge: 'Live', badgeCls: 'badge-live', tagLabel: 'Sales', tagCls: 'tag-blue' },
                { name: 'Operra Tasks', desc: 'Kanban and list views, task assignments, deadlines, and team workload management.', badge: 'Live', badgeCls: 'badge-live', tagLabel: 'Productivity', tagCls: 'tag-green' },
                { name: 'Operra Invoicing', desc: 'Create, send, and track invoices. Automated payment reminders and accounting exports.', badge: 'Live', badgeCls: 'badge-live', tagLabel: 'Finance', tagCls: 'tag-amber' },
                { name: 'Operra Analytics', desc: 'Business intelligence dashboards with real-time KPIs, revenue trends, and team metrics.', badge: 'Live', badgeCls: 'badge-live', tagLabel: 'Insights', tagCls: 'tag-blue' },
                { name: 'Operra Inbox', desc: 'Unified notifications across all modules. Priority-filtered, digest mode, and integrations.', badge: 'Beta', badgeCls: 'badge-beta', tagLabel: 'Comms', tagCls: '' },
                { name: 'Operra Docs', desc: 'Attach documents, proposals, and notes directly to clients, deals, or tasks.', badge: 'Beta', badgeCls: 'badge-beta', tagLabel: 'Storage', tagCls: '' },
                { name: 'Operra API', desc: 'REST API and webhooks to connect Operra to any tool in your stack.', badge: 'Live', badgeCls: 'badge-live', tagLabel: 'Integrations', tagCls: 'tag-blue' },
                { name: 'Operra Mobile', desc: 'iOS and Android app — your full dashboard, tasks, and CRM on the go.', badge: 'Soon', badgeCls: 'badge-soon', tagLabel: 'Mobile', tagCls: '' },
              ].map((p) => (
                <a href="#" className="product-card" key={p.name}>
                  <div className="product-name">{p.name}</div>
                  <p className="product-desc">{p.desc}</p>
                  <div className="product-meta">
                    <span className={`product-badge ${p.badgeCls}`}>{p.badge}</span>
                    <span className={`tag ${p.tagCls}`}>{p.tagLabel}</span>
                  </div>
                </a>
              ))}
            </div>
          </div>
        </section>

        {/* ── HOW IT WORKS ── */}
        <section className="how-section" id="how-it-works">
          <div className="container">
            <div className="section-label">How It Works</div>
            <h2 className="section-title" style={{ marginBottom: '3rem' }}>
              Up and running in <span style={{ color: 'var(--brand-accent)' }}>under a day</span>
            </h2>

            <div className="how-grid">
              <div className="how-steps">
                {[
                  { num: '01', h: 'Import your data', p: 'Bring in contacts from your spreadsheets, CRM exports, or email. Operra maps and cleans it automatically.' },
                  { num: '02', h: 'Set up your workspace', p: 'Configure your pipeline stages, task categories, and invoice templates. Takes minutes, not days.' },
                  { num: '03', h: 'Invite your team', p: 'Add team members with role-based access. Everyone sees exactly what they need — nothing more, nothing less.' },
                  { num: '04', h: 'Run your business', p: 'From your dashboard, manage every client, task, and payment in one place. Your team stays aligned, automatically.' },
                ].map((s) => (
                  <div className="step" key={s.num}>
                    <div className="step-num">{s.num}</div>
                    <div className="step-content">
                      <h4>{s.h}</h4>
                      <p>{s.p}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="how-visual">
                <div className="how-visual-title">Median time to first invoice sent</div>
                <div className="metric-number"><span>4</span> Hours</div>
                <div className="metric-unit">vs. days of setup on traditional platforms</div>
                <div className="compare-bar">
                  <div className="bar-row">
                    <span className="bar-label active">Operra</span>
                    <div className="bar-track">
                      <div className="bar-fill" style={{ width: '16%', background: 'var(--brand-accent)' }} />
                    </div>
                    <span className="bar-val active">4h</span>
                  </div>
                  <div className="bar-row">
                    <span className="bar-label">Salesforce</span>
                    <div className="bar-track">
                      <div className="bar-fill" style={{ width: '65%', background: 'var(--border-dark)' }} />
                    </div>
                    <span className="bar-val">3w</span>
                  </div>
                  <div className="bar-row">
                    <span className="bar-label">DIY Stack</span>
                    <div className="bar-track">
                      <div className="bar-fill" style={{ width: '100%', background: 'var(--danger)' }} />
                    </div>
                    <span className="bar-val" style={{ color: 'var(--danger)' }}>8w+</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── COMPARE ── */}
        <section className="compare-section" id="compare">
          <div className="container">
            <div className="section-label">Compare</div>
            <h2 className="section-title">Why teams choose Operra</h2>
            <p className="section-desc" style={{ marginBottom: '0.5rem' }}>
              One platform. No integration tax. No switching between six tools.
            </p>

            <div className="bench-table-wrap">
              <table className="bench-table">
                <thead>
                  <tr>
                    <th>Capability</th>
                    <th>Operra</th>
                    <th>Salesforce</th>
                    <th>HubSpot</th>
                    <th>Notion + extras</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="bench-highlight">
                    <td>CRM + Tasks + Invoicing in one</td>
                    <td className="bench-winner">✓ All-in-one</td>
                    <td>CRM only</td>
                    <td>CRM + partial</td>
                    <td>Tasks only</td>
                  </tr>
                  <tr>
                    <td>Setup time</td>
                    <td className="bench-winner">&lt; 1 day</td>
                    <td>2–8 weeks</td>
                    <td>1–2 weeks</td>
                    <td>1–3 weeks</td>
                  </tr>
                  <tr className="bench-highlight">
                    <td>Unified dashboard</td>
                    <td className="check">✓</td>
                    <td className="cross">✗</td>
                    <td className="cross">✗</td>
                    <td className="cross">✗</td>
                  </tr>
                  <tr>
                    <td>Built-in invoicing</td>
                    <td className="check">✓</td>
                    <td className="cross">✗</td>
                    <td className="cross">✗</td>
                    <td className="cross">✗</td>
                  </tr>
                  <tr className="bench-highlight">
                    <td>Free tier available</td>
                    <td className="check">✓</td>
                    <td className="cross">✗</td>
                    <td className="check">✓</td>
                    <td className="check">✓</td>
                  </tr>
                  <tr>
                    <td>Starting price / seat</td>
                    <td className="bench-winner">$0 – $29</td>
                    <td>$25 – $300+</td>
                    <td>$0 – $120+</td>
                    <td>$8 – $50+</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* ── CTA ── */}
        <section className="cta-section">
          <div className="container">
            <h2>
              Ready for <span>one system</span><br />
              that does it all?
            </h2>
            <p>Free tier. No credit card. Full platform from day one.</p>
            <div className="hero-actions">
              <Link href="/signup" className="btn btn-primary btn-lg">Create Free Account →</Link>
              <a href="#how-it-works" className="btn btn-ghost btn-lg">Book a Demo</a>
            </div>
          </div>
        </section>

      </main>
      <Footer />
    </>
  )
}
