import { createClient } from "@/lib/supabase-server";
import { redirect } from "next/navigation";
import Link from "next/link";
import { Bell, CheckCheck, ExternalLink } from "lucide-react";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Notifications | ValueWeave",
  robots: { index: false, follow: false },
};

const TYPE_COLORS = {
  opportunity:   "bg-green-100 text-green-700",
  collaborator:  "bg-purple-100 text-purple-700",
  research:      "bg-blue-100 text-blue-700",
  district:      "bg-teal-100 text-teal-700",
  announcement:  "bg-amber-100 text-amber-700",
  general:       "bg-stone-100 text-stone-500",
};

async function getNotifications() {
  const sb = createClient();
  const { data: { user } } = await sb.auth.getUser();
  if (!user) return null;

  // Mark all as read
  await sb.from("notifications")
    .update({ is_read: true })
    .eq("user_id", user.id)
    .eq("is_read", false);

  const { data } = await sb
    .from("notifications")
    .select("*")
    .eq("user_id", user.id)
    .order("created_at", { ascending: false })
    .limit(100);

  return { userId: user.id, notifications: data || [] };
}

function timeAgo(ts) {
  const diff = Date.now() - new Date(ts).getTime();
  const mins  = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days  = Math.floor(diff / 86400000);
  if (mins < 2)  return "just now";
  if (mins < 60) return `${mins}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return `${days}d ago`;
}

export default async function NotificationsPage() {
  const result = await getNotifications();
  if (!result) redirect("/signin");

  const { notifications } = result;

  return (
    <div className="min-h-screen bg-stone-50">
      <div className="max-w-2xl mx-auto px-4 py-10">

        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center">
            <Bell size={18} className="text-amber-600" />
          </div>
          <div>
            <h1 className="font-display font-extrabold text-xl text-ink">Notifications</h1>
            <p className="text-[12px] text-stone-400">{notifications.length} total</p>
          </div>
        </div>

        {notifications.length === 0 ? (
          <div className="card-base p-10 text-center">
            <CheckCheck size={36} className="text-stone-200 mx-auto mb-3" />
            <p className="font-display font-bold text-stone-400">All caught up!</p>
            <p className="text-[13px] text-stone-300 mt-1">No notifications yet.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {notifications.map((n) => (
              <div key={n.id} className="card-base p-4 flex items-start gap-3">
                <div className={`chip text-[10px] font-bold shrink-0 mt-0.5 ${TYPE_COLORS[n.type] || TYPE_COLORS.general}`}>
                  {n.type.toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-display font-semibold text-ink text-sm">{n.title}</p>
                  {n.message && <p className="text-[13px] text-stone-500 mt-0.5">{n.message}</p>}
                  <p className="text-[11px] text-stone-300 mt-1">{timeAgo(n.created_at)}</p>
                </div>
                {n.link && (
                  <Link href={n.link} className="shrink-0 text-amber-500 hover:text-amber-700 transition-colors p-1">
                    <ExternalLink size={14} />
                  </Link>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="mt-8 text-center">
          <Link href="/dashboard" className="btn-ghost text-sm">← Back to dashboard</Link>
        </div>
      </div>
    </div>
  );
}
