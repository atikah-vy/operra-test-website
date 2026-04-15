import { ResourcePage, StatusBadge } from "@/components/dashboard/ResourcePage"

interface SocialPost {
  id: string
  platform: string
  content: string
  scheduled_at: string | null
  status: string
}

export default function SocialPage() {
  return (
    <ResourcePage<SocialPost>
      title="Social"
      description="Posts scheduled and published via Metricool."
      endpoint="/api/v1/social"
      emptyTitle="No posts yet"
      emptyDescription="Create your first scheduled post to see it here."
      addLabel="New post"
      columns={["Platform", "Content", "Scheduled", "Status"]}
      renderRow={(p) => (
        <>
          <td className="py-2 pr-4 font-medium text-slate-900 capitalize">{p.platform}</td>
          <td className="py-2 pr-4 text-slate-700 max-w-md truncate">{p.content}</td>
          <td className="py-2 pr-4 text-slate-500">
            {p.scheduled_at ? new Date(p.scheduled_at).toLocaleString() : "—"}
          </td>
          <td className="py-2 pr-4"><StatusBadge status={p.status} /></td>
        </>
      )}
    />
  )
}
