import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@operra/ui/card"
import { EmptyState } from "@operra/ui/empty-state"
import { Button } from "@operra/ui/button"
import { Badge } from "@operra/ui/badge"
import { Inbox, Plus } from "lucide-react"
import { api, ApiError } from "@/lib/api-client"

interface ResourcePageProps<Item> {
  title: string
  description: string
  endpoint: string
  emptyTitle: string
  emptyDescription: string
  addLabel?: string
  renderRow: (item: Item) => React.ReactNode
  columns: string[]
}

interface Paginated<T> {
  items: T[]
  total: number
}

export async function ResourcePage<Item extends { id: string }>({
  title,
  description,
  endpoint,
  emptyTitle,
  emptyDescription,
  addLabel,
  renderRow,
  columns
}: ResourcePageProps<Item>) {
  let data: Paginated<Item> | null = null
  let error: string | null = null

  try {
    data = await api<Paginated<Item>>(endpoint, { revalidate: 15 })
  } catch (err) {
    error =
      err instanceof ApiError
        ? `API error (${err.status})`
        : err instanceof Error
          ? err.message
          : "Unknown error"
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-brand-primary">{title}</h1>
          <p className="mt-1 text-sm text-slate-500">{description}</p>
        </div>
        {addLabel ? (
          <Button>
            <Plus className="h-4 w-4" />
            {addLabel}
          </Button>
        ) : null}
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">{title}</CardTitle>
          {data ? (
            <CardDescription>
              {data.total} {data.total === 1 ? "record" : "records"}
            </CardDescription>
          ) : null}
        </CardHeader>
        <CardContent>
          {error ? (
            <EmptyState
              icon={<Inbox className="h-8 w-8" />}
              title="Couldn’t load data"
              description={error}
            />
          ) : !data || data.items.length === 0 ? (
            <EmptyState
              icon={<Inbox className="h-8 w-8" />}
              title={emptyTitle}
              description={emptyDescription}
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-left">
                    {columns.map((c) => (
                      <th key={c} className="py-2 pr-4 font-medium text-slate-500">
                        {c}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((item) => (
                    <tr key={item.id} className="border-b border-slate-100 last:border-b-0">
                      {renderRow(item)}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export function StatusBadge({ status }: { status: string }) {
  const variant =
    status === "active" || status === "paid" || status === "converted" || status === "published" || status === "confirmed"
      ? "success"
      : status === "overdue" || status === "failed" || status === "cancelled" || status === "lost" || status === "churned"
        ? "error"
        : status === "pending" || status === "draft" || status === "scheduled" || status === "new"
          ? "info"
          : "secondary"
  return <Badge variant={variant}>{status}</Badge>
}
