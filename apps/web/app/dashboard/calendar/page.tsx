import { ResourcePage, StatusBadge } from "@/components/dashboard/ResourcePage"

interface Booking {
  id: string
  title: string
  start_time: string
  end_time: string
  status: string
  client_id: string | null
}

export default function CalendarPage() {
  return (
    <ResourcePage<Booking>
      title="Calendar"
      description="Upcoming and past bookings synced from Cal.com."
      endpoint="/api/v1/bookings"
      emptyTitle="Nothing scheduled"
      emptyDescription="Connect Cal.com from Settings to sync bookings automatically."
      columns={["Title", "Start", "End", "Status"]}
      renderRow={(b) => (
        <>
          <td className="py-2 pr-4 font-medium text-slate-900">{b.title}</td>
          <td className="py-2 pr-4 text-slate-700">{new Date(b.start_time).toLocaleString()}</td>
          <td className="py-2 pr-4 text-slate-700">{new Date(b.end_time).toLocaleString()}</td>
          <td className="py-2 pr-4"><StatusBadge status={b.status} /></td>
        </>
      )}
    />
  )
}
