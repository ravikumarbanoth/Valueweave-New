// Reusable admin navigation hub — 2-col on mobile, 3-col on desktop.
// Pass currentPath to highlight the active page.

import Link from "next/link";
import {
  BarChart3, Bell, Search, TrendingUp, Brain, Layers, Star,
  Globe, MapPin, Grid, Zap, Target, Users, BookOpen, FileText, Activity,
  Megaphone, Clock, Wrench, Bot, SlidersHorizontal,
} from "lucide-react";

const ADMIN_LINKS = [
  { href: "/admin",                          icon: Grid,     label: "Control Center",          chip: "HOME",      accent: "amber" },
  { href: "/admin/analytics",                icon: BarChart3,label: "Analytics",               chip: "STATS",     accent: "amber" },
  { href: "/admin/search-intelligence",      icon: Search,   label: "Search Intelligence",     chip: "SEARCH",    accent: "blue" },
  { href: "/admin/demand-index",             icon: TrendingUp,label: "Demand Index",           chip: "DEMAND",    accent: "amber" },
  { href: "/admin/intent",                   icon: Brain,    label: "User Intent",             chip: "INTENT",    accent: "teal" },
  { href: "/admin/content-opportunities",    icon: Layers,   label: "Content Opportunities",   chip: "GAPS",      accent: "blue" },
  { href: "/admin/recommendations",          icon: Star,     label: "Recommendations",         chip: "AI",        accent: "green" },
  { href: "/admin/seo",                      icon: Globe,    label: "SEO Command Center",      chip: "SEO",       accent: "green" },
  { href: "/admin/geo",                      icon: Bot,      label: "GEO Audit",               chip: "GEO",       accent: "blue" },
  { href: "/admin/districts",                icon: MapPin,   label: "District Intelligence",   chip: "DISTRICTS", accent: "purple" },
  { href: "/admin/district-opportunity-index",icon: Target,  label: "District Opp. Index",    chip: "RANKED",    accent: "blue" },
  { href: "/admin/opportunity-generator",    icon: Zap,      label: "Opportunity Generator",   chip: "GENERATE",  accent: "amber" },
  { href: "/admin/opportunity-performance",  icon: Activity, label: "Opp. Performance",        chip: "PERF",      accent: "teal" },
  { href: "/admin/matches",                  icon: Users,    label: "Founder Matches",         chip: "MATCHING",  accent: "rose" },
  { href: "/admin/research-performance",     icon: BookOpen, label: "Research Performance",    chip: "CONTENT",   accent: "teal" },
  { href: "/admin/research",                 icon: FileText, label: "Research Publisher",      chip: "PUBLISH",   accent: "stone" },
  { href: "/admin/notifications",            icon: Bell,     label: "Notifications",           chip: "ALERTS",    accent: "rose" },
  { href: "/admin/engagement",               icon: Activity, label: "Engagement Center",        chip: "ENGAGE",    accent: "teal" },
  { href: "/admin/retention",                icon: Clock,    label: "Re-Engagement",            chip: "RETAIN",    accent: "blue" },
  { href: "/admin/announcements",            icon: Megaphone,label: "Announcements",            chip: "ANNOUNCE",  accent: "amber" },
  { href: "/admin/devops",                   icon: SlidersHorizontal, label: "DevOps Control", chip: "CONFIG",    accent: "purple" },
  { href: "/admin/tools",                    icon: Wrench,   label: "Command Center",           chip: "TOOLS",     accent: "stone" },
];

const CHIP_COLORS = {
  amber:  "bg-amber-100 text-amber-700",
  teal:   "bg-teal-100 text-teal-700",
  blue:   "bg-blue-100 text-blue-700",
  green:  "bg-green-100 text-green-700",
  purple: "bg-purple-100 text-purple-700",
  rose:   "bg-rose-100 text-rose-700",
  stone:  "bg-stone-100 text-stone-600",
};

const ICON_COLORS = {
  amber:  "bg-amber-50 text-amber-600",
  teal:   "bg-teal-50 text-teal-600",
  blue:   "bg-blue-50 text-blue-600",
  green:  "bg-green-50 text-green-600",
  purple: "bg-purple-50 text-purple-600",
  rose:   "bg-rose-50 text-rose-600",
  stone:  "bg-stone-50 text-stone-500",
};

export default function AdminQuickAccess({ currentPath = "" }) {
  return (
    <div>
      <h2 className="font-display font-bold text-sm text-ink mb-3 flex items-center gap-2">
        <Grid size={14} className="text-amber-500" />
        Quick Access — All Admin Tools
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2.5">
        {ADMIN_LINKS.map(({ href, icon: Icon, label, chip, accent }) => {
          const isActive = currentPath === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 p-3 rounded-xl border transition-all group ${
                isActive
                  ? "bg-amber-50 border-amber-300 shadow-sm"
                  : "bg-white border-stone-150 hover:border-amber-200 hover:shadow-sm"
              }`}
            >
              <div className={`shrink-0 w-8 h-8 flex items-center justify-center rounded-lg ${ICON_COLORS[accent]}`}>
                <Icon size={14} />
              </div>
              <div className="min-w-0 flex-1">
                <p className={`text-[12px] font-semibold leading-tight truncate transition-colors ${
                  isActive ? "text-amber-700" : "text-ink group-hover:text-amber-700"
                }`}>
                  {label}
                </p>
                <span className={`text-[9px] font-bold mt-0.5 px-1.5 py-0.5 rounded-full inline-block ${CHIP_COLORS[accent]}`}>
                  {chip}
                </span>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
