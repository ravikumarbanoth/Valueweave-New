"use client";
import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase-browser";
import { Bell, BellOff, Loader2 } from "lucide-react";

export default function SubscribeButton({ type, value, label, compact = false }) {
  const [subscribed, setSubscribed] = useState(null);
  const [loading, setLoading] = useState(false);
  const [userId, setUserId] = useState(null);

  useEffect(() => {
    const sb = createClient();
    (async () => {
      const { data: { user } } = await sb.auth.getUser();
      if (!user) { setSubscribed(false); return; }
      setUserId(user.id);
      const { data } = await sb
        .from("subscriptions")
        .select("id")
        .eq("user_id", user.id)
        .eq("type", type)
        .eq("value", value)
        .maybeSingle();
      setSubscribed(!!data);
    })();
  }, [type, value]);

  async function toggle() {
    if (!userId) return;
    setLoading(true);
    const sb = createClient();
    if (subscribed) {
      await sb.from("subscriptions").delete()
        .eq("user_id", userId).eq("type", type).eq("value", value);
      setSubscribed(false);
    } else {
      await sb.from("subscriptions").insert({ user_id: userId, type, value });
      setSubscribed(true);
    }
    setLoading(false);
  }

  if (subscribed === null) return null;
  if (!userId) return null;

  const Icon = loading ? Loader2 : subscribed ? BellOff : Bell;

  if (compact) {
    return (
      <button
        onClick={toggle}
        disabled={loading}
        title={subscribed ? `Unfollow ${label || value}` : `Follow ${label || value}`}
        className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[12px] font-semibold transition-colors ${
          subscribed
            ? "bg-amber-100 text-amber-700 hover:bg-amber-200"
            : "bg-stone-100 text-stone-500 hover:bg-amber-50 hover:text-amber-600"
        }`}
      >
        <Icon size={12} className={loading ? "animate-spin" : ""} />
        {subscribed ? "Following" : "Follow"}
      </button>
    );
  }

  return (
    <button
      onClick={toggle}
      disabled={loading}
      className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-colors ${
        subscribed
          ? "bg-amber-100 text-amber-700 border border-amber-200 hover:bg-amber-200"
          : "bg-white border border-stone-200 text-stone-600 hover:border-amber-300 hover:text-amber-700 hover:bg-amber-50"
      }`}
    >
      <Icon size={14} className={loading ? "animate-spin" : ""} />
      {subscribed ? `Following ${label || value}` : `Follow ${label || value}`}
    </button>
  );
}
