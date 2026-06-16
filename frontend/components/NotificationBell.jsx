"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase-browser";
import { Bell } from "lucide-react";

export default function NotificationBell() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const sb = createClient();
    (async () => {
      const { data: { user } } = await sb.auth.getUser();
      if (!user) return;
      const { count: c } = await sb
        .from("notifications")
        .select("*", { count: "exact", head: true })
        .eq("user_id", user.id)
        .eq("is_read", false);
      setCount(c || 0);
    })();
  }, []);

  return (
    <Link
      href="/notifications"
      aria-label={count > 0 ? `${count} unread notifications` : "Notifications"}
      className="relative flex items-center justify-center w-8 h-8 rounded-lg text-muted hover:text-ink hover:bg-stone-100 transition-colors"
    >
      <Bell size={17} />
      {count > 0 && (
        <span className="absolute -top-0.5 -right-0.5 min-w-[16px] h-4 px-0.5 bg-rose-500 text-white text-[9px] font-bold rounded-full flex items-center justify-center leading-none">
          {count > 99 ? "99+" : count}
        </span>
      )}
    </Link>
  );
}
