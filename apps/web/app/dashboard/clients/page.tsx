import { ResourcePage, StatusBadge } from "@/components/dashboard/ResourcePage"

interface Client {
  id: string
  name: string
  company: string | null
  contact_email: string | null
  status: string
  created_at: string
}

export default function ClientsPage() {
  return (
    <ResourcePage<Client>
      title="Clients"
      description="Converted leads and active accounts."
      endpoint="/api/v1/clients"
      emptyTitle="No clients yet"
      emptyDescription="Convert a lead from the Leads page to create your first client."
      addLabel="Add client"
      columns={["Name", "Company", "Contact", "Status", "Created"]}
      renderRow={(c) => (
        <>
          <td className="py-2 pr-4 font-medium text-slate-900">{c.name}</td>
          <td className="py-2 pr-4 text-slate-700">{c.company ?? "—"}</td>
          <td className="py-2 pr-4 text-slate-700">{c.contact_email ?? "—"}</td>
          <td className="py-2 pr-4"><StatusBadge status={c.status} /></td>
          <td className="py-2 pr-4 text-slate-500">
            {new Date(c.created_at).toLocaleDateString()}
          </td>
        </>
      )}
    />
  )
}
