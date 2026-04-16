import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@operra/ui/card"
import { EmptyState } from "@operra/ui/empty-state"
import {
  Users,
  UserCheck,
  DollarSign,
  Calendar,
  ArrowUpRight,
  Inbox,
  Clock,
  BarChart3,
  TrendingUp,
} from "lucide-react"
import { api, ApiError } from "@/lib/api-client"

interface OverviewStats {
  leads_total: number
  leads_new: number
  clients_active: number
  revenue_month: number
  currency: string
  upcoming_bookings: number
}

async function getStats(): Promise<OverviewStats | null> {
  try {
    return await api<OverviewStats>("/api/v1/analytics/overview", { revalidate: 30 })
  } catch (err) {
    if (err instanceof ApiError) return null
    throw err
  }
}

export default async function OverviewPage() {
  const stats = await getStats()

  return (
    <div className="space-y-6">

      {/* ── Welcome banner ─────────────────────────────────────── */}
      <div className="relative overflow-hidden rounded-2xl bg-[#0B1F3A] px-8 py-7">
        {/* gradient overlay */}
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-r from-[#0B1F3A] via-[#1E3A8A]/70 to-[#3B82F6]/40" />
        {/* decorative circles */}
        <div className="pointer-events-none absolute -right-10 -top-10 h-52 w-52 rounded-full bg-[#3B82F6]/10" />
        <div className="pointer-events-none absolute -bottom-8 right-36 h-36 w-36 rounded-full bg-[#60A5FA]/10" />

        <div className="relative">
          <p className="text-sm font-medium text-[#60A5FA]">Welcome back 👋</p>
          <h1 className="mt-1 text-2xl font-bold text-white">Good to see you.</h1>
          <p className="mt-1 text-sm text-[#94A3B8]">
            Here's a live snapshot of your pipeline, clients, and revenue.
          </p>
        </div>

        <div className="relative mt-5 flex flex-wrap gap-2">
          {["CRM", "Leads", "Invoicing", "Bookings", "Analytics"].map((tag) => (
            <span
              key={tag}
              className="rounded-full border border-[#1E3A8A] bg-[#1E3A8A]/40 px-3 py-1 text-xs font-medium text-[#60A5FA]"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* ── Stat cards ─────────────────────────────────────────── */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total Leads"
          value={stats?.leads_total ?? "—"}
          hint={stats ? `+${stats.leads_new} this week` : undefined}
          icon={Users}
          color="blue"
        />
        <StatCard
          label="Active Clients"
          value={stats?.clients_active ?? "—"}
          icon={UserCheck}
          color="green"
        />
        <StatCard
          label="Revenue (month)"
          value={
            stats?.revenue_month != null
              ? `${stats.currency} ${stats.revenue_month.toLocaleString()}`
              : "—"
          }
          icon={DollarSign}
          color="indigo"
        />
        <StatCard
          label="Upcoming Bookings"
          value={stats?.upcoming_bookings ?? "—"}
          icon={Calendar}
          color="amber"
        />
      </div>

      {/* ── Recent activity ────────────────────────────────────── */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card className="border-[#E2E8F0] shadow-none">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-[15px] font-semibold text-[#0F172A]">
                  Recent Leads
                </CardTitle>
                <CardDescription className="mt-0.5 text-xs text-[#64748B]">
                  Latest captured through marketing and partner channels.
                </CardDescription>
              </div>
              <span className="cursor-pointer text-xs font-medium text-[#3B82F6] hover:underline">
                View all →
              </span>
            </div>
          </CardHeader>
          <CardContent>
            <EmptyState
              icon={<Inbox className="h-8 w-8 text-[#94A3B8]" />}
              title="No leads yet"
              description="Leads submitted from your marketing form will land here first."
            />
          </CardContent>
        </Card>

        <Card className="border-[#E2E8F0] shadow-none">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-[15px] font-semibold text-[#0F172A]">
                  Upcoming Events
                </CardTitle>
                <CardDescription className="mt-0.5 text-xs text-[#64748B]">
                  Bookings synced from Cal.com.
                </CardDescription>
              </div>
              <span className="cursor-pointer text-xs font-medium text-[#3B82F6] hover:underline">
                View all →
              </span>
            </div>
          </CardHeader>
          <CardContent>
            <EmptyState
              icon={<Clock className="h-8 w-8 text-[#94A3B8]" />}
              title="Nothing scheduled"
              description="Connect Cal.com from Settings to start syncing your calendar."
            />
          </CardContent>
        </Card>
      </div>

      {/* ── Performance overview ───────────────────────────────── */}
      <Card className="border-[#E2E8F0] shadow-none">
        <CardHeader className="pb-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#EFF6FF]">
              <BarChart3 className="h-4 w-4 text-[#3B82F6]" strokeWidth={1.5} />
            </div>
            <div>
              <CardTitle className="text-[15px] font-semibold text-[#0F172A]">
                Performance Overview
              </CardTitle>
              <CardDescription className="text-xs text-[#64748B]">
                Connect your integrations to unlock live analytics.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            {[
              { label: "Lead Conversion", value: "—", sub: "Connect Apollo", icon: TrendingUp, color: "blue" },
              { label: "Avg Deal Size", value: "—", sub: "Connect Bukku", icon: DollarSign, color: "green" },
              { label: "Social Reach", value: "—", sub: "Connect Metricool", icon: Users, color: "indigo" },
            ].map((item) => {
              const c = colorMap[item.color as keyof typeof colorMap]
              const Icon = item.icon
              return (
                <div
                  key={item.label}
                  className="rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] p-4"
                >
                  <div className={`mb-3 flex h-9 w-9 items-center justify-center rounded-lg ${c.bg}`}>
                    <Icon className={`h-4 w-4 ${c.icon}`} strokeWidth={1.5} />
                  </div>
                  <p className="text-xs font-medium text-[#64748B]">{item.label}</p>
                  <p className="mt-1 text-2xl font-bold text-[#0F172A]">{item.value}</p>
                  <p className="mt-1 text-xs text-[#94A3B8]">{item.sub}</p>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

    </div>
  )
}

/* ─── Colour tokens ──────────────────────────────────────────── */
const colorMap = {
  blue:   { bg: "bg-[#EFF6FF]", icon: "text-[#3B82F6]", badge: "bg-[#DBEAFE] text-[#1E3A8A]" },
  green:  { bg: "bg-[#F0FDF4]", icon: "text-[#22C55E]", badge: "bg-[#DCFCE7] text-[#166534]" },
  indigo: { bg: "bg-[#EEF2FF]", icon: "text-[#6366F1]", badge: "bg-[#E0E7FF] text-[#3730A3]" },
  amber:  { bg: "bg-[#FFFBEB]", icon: "text-[#F59E0B]", badge: "bg-[#FEF3C7] text-[#92400E]" },
}

/* ─── StatCard ───────────────────────────────────────────────── */
function StatCard({
  label,
  value,
  hint,
  icon: Icon,
  color,
}: {
  label: string
  value: React.ReactNode
  hint?: string
  icon: React.ElementType
  color: keyof typeof colorMap
}) {
  const c = colorMap[color]
  return (
    <Card className="border-[#E2E8F0] shadow-none">
      <CardContent className="pb-5 pt-5">
        <div className="flex items-start justify-between">
          <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${c.bg}`}>
            <Icon className={`h-5 w-5 ${c.icon}`} strokeWidth={1.5} />
          </div>
          {hint && (
            <span className={`flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${c.badge}`}>
              <ArrowUpRight className="h-3 w-3" />
              {hint}
            </span>
          )}
        </div>
        <div className="mt-4">
          <p className="text-xs font-medium text-[#64748B]">{label}</p>
          <p className="mt-1 text-2xl font-bold text-[#0F172A]">{value}</p>
        </div>
      </CardContent>
    </Card>
  )
}
