import Link from "next/link"
import { OrganizationSwitcher, UserButton } from "@clerk/nextjs"
import {
  LayoutDashboard,
  Users,
  UserCheck,
  Calendar,
  Share2,
  Receipt,
  Zap,
  Settings
} from "lucide-react"
import { requireAuth } from "@/lib/auth"

const navItems = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/leads", label: "Leads", icon: Users },
  { href: "/dashboard/clients", label: "Clients", icon: UserCheck },
  { href: "/dashboard/calendar", label: "Calendar", icon: Calendar },
  { href: "/dashboard/social", label: "Social", icon: Share2 },
  { href: "/dashboard/finance", label: "Finance", icon: Receipt },
  { href: "/dashboard/automations", label: "Automations", icon: Zap },
  { href: "/dashboard/settings", label: "Settings", icon: Settings }
]

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  await requireAuth()

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="hidden w-60 shrink-0 flex-col border-r border-slate-200 bg-white lg:flex">
        <div className="flex h-16 items-center gap-2 border-b border-slate-200 px-6">
          <span className="text-lg font-bold tracking-tight text-brand-primary">Operra</span>
        </div>
        <nav className="flex flex-1 flex-col gap-1 p-4">
          {navItems.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900"
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          ))}
        </nav>
      </aside>

      <div className="flex flex-1 flex-col">
        {/* Top bar */}
        <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4 sm:px-6">
          <div className="flex items-center gap-4">
            <OrganizationSwitcher
              afterCreateOrganizationUrl="/dashboard"
              afterSelectOrganizationUrl="/dashboard"
              hidePersonal
              appearance={{ elements: { organizationSwitcherTrigger: "py-1.5 px-3" } }}
            />
          </div>
          <div className="flex items-center gap-4">
            <input
              type="search"
              placeholder="Search…"
              className="hidden h-9 w-64 rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-700 placeholder:text-slate-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent sm:block"
            />
            <UserButton afterSignOutUrl="/" />
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6 lg:p-8">{children}</main>
      </div>
    </div>
  )
}
