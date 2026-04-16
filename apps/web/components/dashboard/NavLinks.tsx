"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import type { LucideIcon } from "lucide-react"

export interface NavItem {
  href: string
  label: string
  icon: LucideIcon
}

export function NavLinks({ items }: { items: NavItem[] }) {
  const pathname = usePathname()

  return (
    <nav className="flex flex-1 flex-col gap-0.5 p-3">
      {items.map(({ href, label, icon: Icon }) => {
        const isActive =
          pathname === href ||
          (href !== "/dashboard" && pathname.startsWith(href))
        return (
          <Link
            key={href}
            href={href}
            className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all ${
              isActive
                ? "bg-[#EFF6FF] text-[#3B82F6]"
                : "text-[#64748B] hover:bg-[#F8FAFC] hover:text-[#0F172A]"
            }`}
          >
            <Icon
              className={`h-4 w-4 flex-shrink-0 transition-colors ${
                isActive ? "text-[#3B82F6]" : "text-[#94A3B8]"
              }`}
              strokeWidth={1.5}
            />
            {label}
          </Link>
        )
      })}
    </nav>
  )
}
