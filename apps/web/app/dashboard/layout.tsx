import Link from "next/link"
import { UserButton } from "@clerk/nextjs"
import {
  LayoutDashboard,
  Users,
  UserCheck,
  Calendar,
  Share2,
  Receipt,
  Zap,
  Settings,
  Bell,
  Search,
} from "lucide-react"
import { requireAuth } from "@/lib/auth"
import { NavLinks } from "@/components/dashboard/NavLinks"

const navItems = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/leads", label: "Leads", icon: Users },
  { href: "/dashboard/clients", label: "Clients", icon: UserCheck },
  { href: "/dashboard/calendar", label: "Calendar", icon: Calendar },
  { href: "/dashboard/social", label: "Social", icon: Share2 },
  { href: "/dashboard/finance", label: "Finance", icon: Receipt },
  { href: "/dashboard/automations", label: "Automations", icon: Zap },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
]

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  await requireAuth()

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      {/* Sidebar */}
      <aside className="hidden w-[220px] shrink-0 flex-col border-r border-[#E2E8F0] bg-white lg:flex">
        {/* Logo */}
        <div className="flex h-16 items-center gap-2.5 border-b border-[#E2E8F0] px-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#3B82F6]">
            <span className="text-xs font-bold text-white">O</span>
          </div>
          <span className="text-[15px] font-bold tracking-tight text-[#0B1F3A]">
            Operra
          </span>
        </div>

        {/* Nav links with active state */}
        <NavLinks items={navItems} />

        {/* Bottom user area */}
        <div className="border-t border-[#E2E8F0] p-3">
          <div className="flex items-center gap-3 rounded-lg px-3 py-2">
            <UserButton afterSignOutUrl="/" />
            <span className="text-sm text-[#64748B]">Account</span>
          </div>
        </div>
      </aside>

      {/* Main column */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top bar */}
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-[#E2E8F0] bg-white px-6">
          {/* Left: mobile logo + search */}
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="flex items-center gap-2 lg:hidden">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#3B82F6]">
                <span className="text-[11px] font-bold text-white">O</span>
              </div>
              <span className="text-sm font-bold text-[#0B1F3A]">Operra</span>
            </Link>
            <div className="relative hidden sm:block">
              <Search
                className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#94A3B8]"
                strokeWidth={1.5}
              />
              <input
                type="search"
                placeholder="Search anything..."
                className="h-9 w-60 rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] pl-9 pr-3 text-sm text-[#0F172A] placeholder:text-[#94A3B8] focus:border-[#3B82F6] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]/20 transition-colors"
              />
            </div>
          </div>

          {/* Right: notifications + avatar */}
          <div className="flex items-center gap-2.5">
            <button className="flex h-9 w-9 items-center justify-center rounded-lg border border-[#E2E8F0] bg-white text-[#64748B] hover:bg-[#F8FAFC] transition-colors">
              <Bell className="h-4 w-4" strokeWidth={1.5} />
            </button>
            <UserButton afterSignOutUrl="/" />
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6 lg:p-8">{children}</main>
      </div>
    </div>
  )
}
