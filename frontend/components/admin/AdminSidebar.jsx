"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase-browser";
import {
  LayoutDashboard, Bell, BarChart3, Search, TrendingUp, Brain,
  Lightbulb, Star, SearchCheck, BookOpen, PenSquare,
  MapPin, Grid, Activity, Zap, Users,
  Megaphone, Clock, Wrench, Bot, SlidersHorizontal, Network, Landmark, Package, Route,
} from "lucide-react";

const GROUPS = [
  { label: "OPERATIONS", items: [ { href: "/admin", label: "Control Center", icon: LayoutDashboard, exact: true }, { href: "/admin/notifications", label: "Notifications", icon: Bell, badge: true } ] },
  { label: "KNOWLEDGE GRAPH", items: [
    { href: "/admin/knowledge-graph", label: "Graph Dashboard", icon: Network },
    { href: "/admin/districts-cms", label: "District CMS", icon: MapPin },
    { href: "/admin/skills", label: "Skills CMS", icon: Wrench },
    { href: "/admin/schemes", label: "Schemes CMS", icon: Landmark },
    { href: "/admin/resources", label: "Resources CMS", icon: Package },
    { href: "/admin/roadmaps", label: "Roadmaps CMS", icon: Route },
    { href: "/admin/opportunity-mapping", label: "Opp. Mapping", icon: Network },
  ] },
  { label: "INTELLIGENCE", items: [ { href: "/admin/analytics", label: "Analytics", icon: BarChart3 }, { href: "/admin/search-intelligence", label: "Search Intelligence", icon: Search }, { href: "/admin/demand-index", label: "Demand Index", icon: TrendingUp }, { href: "/admin/intent", label: "User Intent", icon: Brain } ] },
  { label: "CONTENT", items: [ { href: "/admin/content-opportunities", label: "Content Opportunities", icon: Lightbulb }, { href: "/admin/recommendations", label: "Recommendations", icon: Star }, { href: "/admin/seo", label: "SEO Command", icon: SearchCheck }, { href: "/admin/geo", label: "GEO Audit", icon: Bot }, { href: "/admin/research-performance", label: "Research Perf.", icon: BookOpen }, { href: "/admin/research", label: "Research Publisher", icon: PenSquare } ] },
  { label: "ENGAGEMENT", items: [ { href: "/admin/engagement", label: "Engagement Center", icon: Activity }, { href: "/admin/retention", label: "Re-Engagement", icon: Clock }, { href: "/admin/announcements", label: "Announcements", icon: Megaphone } ] },
  { label: "PLATFORM", items: [ { href: "/admin/devops", label: "DevOps Control", icon: SlidersHorizontal }, { href: "/admin/districts", label: "Districts", icon: MapPin }, { href: "/admin/district-opportunity-index", label: "District Opp. Index", icon: Grid }, { href: "/admin/opportunity-performance", label: "Opp. Performance", icon: Activity }, { href: "/admin/opportunity-generator", label: "Opp. Generator", icon: Zap }, { href: "/admin/matches", label: "Founder Matches", icon: Users } ] },
  { label: "TOOLS", items: [ { href: "/admin/tools", label: "Command Center", icon: Wrench } ] },
];

export default function AdminSidebar() {
  const pathname = usePathname();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    async function fetchUnread() {
      try {
        const sb = createClient();
        const { count } = await sb.from("admin_notifications").select("*", { count: "exact", head: true }).eq("status", "unread");
        setUnreadCount(count || 0);
      } catch {}
    }
    fetchUnread();
  }, [pathname]);

  return (
    <aside className="w-56 shrink-0 min-h-[calc(100vh-64px)] bg-white border-r border-stone-200 hidden lg:flex flex-col">
      <div className="p-3 border-b border-stone-100"><span className="chip bg-amber-100 text-amber-700 border border-amber-200 text-[10px]">ADMIN PANEL</span><p className="text-[10px] text-stone-400 mt-1 font-medium">ValueWeave Intelligence Platform</p></div>
      <nav className="flex-1 p-2 overflow-y-auto space-y-3">
        {GROUPS.map(({ label, items }) => <div key={label}><p className="text-[9px] font-bold text-stone-300 uppercase tracking-widest px-2 mb-1">{label}</p>{items.map(({ href, label: itemLabel, icon: Icon, exact, badge }) => { const active = exact ? pathname === href : pathname.startsWith(href); return <Link key={href} href={href} className={`flex items-center gap-2 px-2.5 py-2 rounded-xl text-[12px] font-semibold transition-colors mb-0.5 ${active ? "bg-amber-50 text-amber-700 border border-amber-200" : "text-stone-500 hover:bg-stone-50 hover:text-ink"}`}><Icon size={13} className={active ? "text-amber-600" : "text-stone-400"} /><span className="flex-1 truncate">{itemLabel}</span>{badge && unreadCount > 0 && <span className="bg-red-500 text-white text-[9px] font-bold px-1.5 py-0.5 rounded-full min-w-[16px] text-center">{unreadCount > 99 ? "99+" : unreadCount}</span>}</Link>; })}</div>)}
      </nav>
      <div className="p-3 border-t border-stone-100"><p className="text-[9px] text-stone-300 font-medium">Knowledge Graph Foundation</p></div>
    </aside>
  );
}
