import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@operra/ui/card"
import { Badge } from "@operra/ui/badge"

const integrations = [
  { key: "attio", label: "Attio (CRM)", envVar: "ATTIO_API_KEY" },
  { key: "apollo", label: "Apollo (Enrichment)", envVar: "APOLLO_API_KEY" },
  { key: "metricool", label: "Metricool (Social)", envVar: "METRICOOL_API_TOKEN" },
  { key: "bukku", label: "Bukku (Accounting)", envVar: "BUKKU_API_KEY" },
  { key: "calcom", label: "Cal.com (Booking)", envVar: "CALCOM_API_KEY" },
  { key: "meta", label: "Meta (Instagram)", envVar: "META_APP_SECRET" }
]

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-brand-primary">Settings</h1>
        <p className="mt-1 text-sm text-slate-500">
          Manage integrations, API keys, and organization preferences.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Integrations</CardTitle>
          <CardDescription>
            Configure API credentials via environment variables on the FastAPI service.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {integrations.map((int) => (
            <div
              key={int.key}
              className="flex items-center justify-between rounded-md border border-slate-200 px-4 py-3"
            >
              <div>
                <div className="text-sm font-medium text-slate-900">{int.label}</div>
                <div className="text-xs text-slate-500">
                  Set <code className="rounded bg-slate-100 px-1">{int.envVar}</code> to enable
                </div>
              </div>
              <Badge variant="secondary">Not configured</Badge>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
