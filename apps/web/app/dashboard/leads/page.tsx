import { ResourcePage, StatusBadge } from "@/components/dashboard/ResourcePage"

interface Lead {
  id: string
  email: string
  first_name: string | null
  last_name: string | null
  company: string | null
  source: string
  status: string
  created_at: string
}

export default function LeadsPage() {
  return (
    <ResourcePage<Lead>
      title="Leads"
      description="Prospects captured from your marketing channels."
      endpoint="/api/v1/leads"
      emptyTitle="No leads yet"
      emptyDescription="They'll appear here as soon as someone submits the marketing form."
      addLabel="Add lead"
      columns={["Name", "Email", "Company", "Source", "Status", "Created"]}
      renderRow={(l) => (
        <>
          <td className="py-2 pr-4 font-medium text-slate-900">
            {[l.first_name, l.last_name].filter(Boolean).join(" ") || "—"}
          </td>
          <td className="py-2 pr-4 text-slate-700">{l.email}</td>
          <td className="py-2 pr-4 text-slate-700">{l.company ?? "—"}</td>
          <td className="py-2 pr-4 text-slate-500">{l.source}</td>
          <td className="py-2 pr-4"><StatusBadge status={l.status} /></td>
          <td className="py-2 pr-4 text-slate-500">
            {new Date(l.created_at).toLocaleDateString()}
          </td>
        </>
      )}
    />
  )
}
