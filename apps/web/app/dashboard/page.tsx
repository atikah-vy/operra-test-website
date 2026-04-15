import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@operra/ui/card"
import { EmptyState } from "@operra/ui/empty-state"
import { Inbox } from "lucide-react"
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
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-brand-primary">Overview</h1>
        <p className="mt-1 text-sm text-slate-500">
          Live snapshot of your pipeline, clients, and revenue.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Leads" value={stats?.leads_total ?? "—"} hint={stats ? `${stats.leads_new} new this week` : undefined} />
        <StatCard label="Active Clients" value={stats?.clients_active ?? "—"} />
        <StatCard
          label="Revenue (month)"
          value={stats ? `${stats.currency} ${stats.revenue_month.toLocaleString()}` : "—"}
        />
        <StatCard label="Upcoming Bookings" value={stats?.upcoming_bookings ?? "—"} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Leads</CardTitle>
            <CardDescription>Latest captured through marketing and partner channels.</CardDescription>
          </CardHeader>
          <CardContent>
            <EmptyState
              icon={<Inbox className="h-8 w-8" />}
              title="No leads yet"
              description="Leads submitted from your marketing form will land here first."
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Upcoming Events</CardTitle>
            <CardDescription>Bookings synced from Cal.com.</CardDescription>
          </CardHeader>
          <CardContent>
            <EmptyState
              icon={<Inbox className="h-8 w-8" />}
              title="Nothing scheduled"
              description="Connect Cal.com from Settings to start syncing your calendar."
            />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function StatCard({
  label,
  value,
  hint
}: {
  label: string
  value: React.ReactNode
  hint?: string
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{label}</CardDescription>
        <CardTitle className="text-3xl">{value}</CardTitle>
      </CardHeader>
      {hint ? (
        <CardContent>
          <span className="text-xs text-slate-500">{hint}</span>
        </CardContent>
      ) : null}
    </Card>
  )
}
