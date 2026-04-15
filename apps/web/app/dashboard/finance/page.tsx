import { ResourcePage, StatusBadge } from "@/components/dashboard/ResourcePage"

interface Invoice {
  id: string
  client_id: string
  invoice_number: string
  amount: number
  currency: string
  status: string
  issued_at: string | null
  due_at: string | null
}

export default function FinancePage() {
  return (
    <ResourcePage<Invoice>
      title="Finance"
      description="Invoices and cash flow, synced with Bukku."
      endpoint="/api/v1/invoices"
      emptyTitle="No invoices yet"
      emptyDescription="Create an invoice to kick off your first billing cycle."
      addLabel="New invoice"
      columns={["Invoice", "Amount", "Status", "Issued", "Due"]}
      renderRow={(i) => (
        <>
          <td className="py-2 pr-4 font-medium text-slate-900">{i.invoice_number}</td>
          <td className="py-2 pr-4 text-slate-700">
            {i.currency} {i.amount.toLocaleString()}
          </td>
          <td className="py-2 pr-4"><StatusBadge status={i.status} /></td>
          <td className="py-2 pr-4 text-slate-500">
            {i.issued_at ? new Date(i.issued_at).toLocaleDateString() : "—"}
          </td>
          <td className="py-2 pr-4 text-slate-500">
            {i.due_at ? new Date(i.due_at).toLocaleDateString() : "—"}
          </td>
        </>
      )}
    />
  )
}
