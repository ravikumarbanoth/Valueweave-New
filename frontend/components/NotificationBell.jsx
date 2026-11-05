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
      //: 44px, not 32. Measuring the signed-in mobile header to check the
      //: overlap fix showed this was the one control in the row still under
      //: the tap minimum PX Phase 10 set for the whole public site — the
      //: search, YouTube and avatar controls beside it are all 44. The glyph
      //: is unchanged at 17px; only the touchable box grew, and rounded-2xl
      //: matches the tiles it now sits between.
      className="relative flex items-center justify-center w-11 h-11 min-h-[44px] min-w-[44px] rounded-2xl text-muted hover:text-ink hover:bg-stone-100 transition-colors"
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
