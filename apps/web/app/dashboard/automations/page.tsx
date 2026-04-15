import { ResourcePage } from "@/components/dashboard/ResourcePage"
import { Badge } from "@operra/ui/badge"

interface Automation {
  id: string
  name: string
  is_active: boolean
  run_count: number
  created_at: string
}

export default function AutomationsPage() {
  return (
    <ResourcePage<Automation>
      title="Automations"
      description="Workflow rules that trigger actions across your modules."
      endpoint="/api/v1/automations"
      emptyTitle="No automations yet"
      emptyDescription="Create rules to auto-enrich leads, sync to CRM, send notifications, and more."
      addLabel="New automation"
      columns={["Name", "State", "Runs", "Created"]}
      renderRow={(a) => (
        <>
          <td className="py-2 pr-4 font-medium text-slate-900">{a.name}</td>
          <td className="py-2 pr-4">
            <Badge variant={a.is_active ? "success" : "secondary"}>
              {a.is_active ? "active" : "paused"}
            </Badge>
          </td>
          <td className="py-2 pr-4 text-slate-700">{a.run_count}</td>
          <td className="py-2 pr-4 text-slate-500">
            {new Date(a.created_at).toLocaleDateString()}
          </td>
        </>
      )}
    />
  )
}
