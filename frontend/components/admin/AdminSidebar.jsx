"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  BarChart3,
  Brain,
  Lightbulb,
  SearchCheck,
  MapPin,
  Zap,
  Users,
  BookOpen,
  PenSquare,
} from "lucide-react";

const NAV = [
  { href: "/admin", label: "Control Center", icon: LayoutDashboard, exact: true },
  { href: "/admin/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/admin/intent", label: "User Intent", icon: Brain },
  { href: "/admin/content-opportunities", label: "Content Opportunities", icon: Lightbulb },
  { href: "/admin/seo", label: "SEO Command", icon: SearchCheck },
  { href: "/admin/districts", label: "Districts", icon: MapPin },
  { href: "/admin/opportunity-generator", label: "Opp. Generator", icon: Zap },
  { href: "/admin/matches", label: "Founder Matches", icon: Users },
  { href: "/admin/research-performance", label: "Research Perf.", icon: BookOpen },
  { href: "/admin/research", label: "Research Publisher", icon: PenSquare },
];

export default function AdminSidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-60 shrink-0 min-h-[calc(100vh-64px)] bg-white border-r border-stone-200 hidden lg:flex flex-col">
      <div className="p-4 border-b border-stone-100">
        <span className="chip bg-amber-100 text-amber-700 border border-amber-200 text-[10px]">
          ADMIN PANEL
        </span>
        <p className="text-[11px] text-stone-400 mt-1 font-medium">ValueWeave Control Center</p>
      </div>

      <nav className="flex-1 p-2 overflow-y-auto">
        {NAV.map(({ href, label, icon: Icon, exact }) => {
          const active = exact ? pathname === href : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-xl text-[13px] font-semibold transition-colors mb-0.5 ${
                active
                  ? "bg-amber-50 text-amber-700 border border-amber-200"
                  : "text-stone-500 hover:bg-stone-50 hover:text-ink"
              }`}
            >
              <Icon size={15} className={active ? "text-amber-600" : "text-stone-400"} />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-stone-100">
        <p className="text-[10px] text-stone-300 font-medium">Phase 3 · Admin Control Center</p>
      </div>
    </aside>
  );
}
