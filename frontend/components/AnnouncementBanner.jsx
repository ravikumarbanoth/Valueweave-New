"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase-browser";
import { X, Megaphone } from "lucide-react";

const PRIORITY_COLORS = {
  high:   "bg-rose-600 text-white",
  normal: "bg-amber-500 text-white",
  low:    "bg-stone-700 text-white",
};

export default function AnnouncementBanner() {
  const [announcements, setAnnouncements] = useState([]);
  const [dismissed, setDismissed] = useState(new Set());

  useEffect(() => {
    const sb = createClient();

    sb.from("platform_settings")
      .select("key,value")
      .in("key", ["maintenance.enabled", "maintenance.text", "announcement.enabled", "announcement.text"])
      .then(({ data }) => {
        const map = Object.fromEntries((data || []).map((row) => [row.key, row.value]));
        const settingsAnnouncements = [];
        if (map["maintenance.enabled"] === true) {
          settingsAnnouncements.push({
            id: "platform-maintenance",
            title: "Maintenance Mode",
            message: map["maintenance.text"] || "Some features may be temporarily unavailable.",
            priority: "high",
          });
        }
        if (map["announcement.enabled"] === true && map["announcement.text"]) {
          settingsAnnouncements.push({
            id: "platform-announcement",
            title: "Important Announcement",
            message: map["announcement.text"],
            priority: "normal",
          });
        }
        if (settingsAnnouncements.length) setAnnouncements((prev) => [...settingsAnnouncements, ...prev]);
      });

    sb.from("announcements")
      .select("id,title,message,link,link_label,priority")
      .eq("is_active", true)
      .order("priority", { ascending: false })
      .limit(3)
      .then(({ data }) => {
        if (!data?.length) return;
        const already = new Set(
          data.map((a) => a.id).filter((id) => {
            try { return sessionStorage.getItem(`vw_banner_${id}`) === "1"; } catch { return false; }
          })
        );
        setDismissed(already);
        setAnnouncements((prev) => [...prev, ...data]);
      });
  }, []);

  function dismiss(id) {
    try { sessionStorage.setItem(`vw_banner_${id}`, "1"); } catch {}
    setDismissed((prev) => new Set([...prev, id]));
  }

  const visible = announcements.filter((a) => !dismissed.has(a.id));
  if (!visible.length) return null;

  // Show only the top undismissed announcement
  const banner = visible[0];
  const colors = PRIORITY_COLORS[banner.priority] || PRIORITY_COLORS.normal;

  return (
    <div className={`${colors} px-4 py-2.5 flex items-center gap-3 text-sm`} role="alert">
      <Megaphone size={14} className="shrink-0 opacity-80" />
      <div className="flex-1 min-w-0">
        <span className="font-semibold">{banner.title}</span>
        {banner.message && (
          <span className="opacity-80 ml-1.5 hidden sm:inline">— {banner.message}</span>
        )}
        {banner.link && (
          <Link
            href={banner.link}
            className="ml-2 underline underline-offset-2 font-semibold hover:opacity-80 shrink-0"
          >
            {banner.link_label || "Learn more"}
          </Link>
        )}
      </div>
      <button
        onClick={() => dismiss(banner.id)}
        aria-label="Dismiss announcement"
        className="shrink-0 opacity-70 hover:opacity-100 transition-opacity p-0.5"
      >
        <X size={14} />
      </button>
    </div>
  );
}
