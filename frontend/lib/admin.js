// ValueWeave — server-side admin check.
// Admin = profiles.is_admin (set via migrations/001_research_articles.sql),
// with the ADMIN_EMAILS env allowlist kept as a bootstrap fallback and
// development mode open for local work. RLS independently enforces writes,
// so this gate is for UX/routing — the database is the security boundary.

import { createClient } from "@/lib/supabase-server";

export async function getAdminStatus() {
  if (process.env.NODE_ENV === "development") {
    return { user: { email: "dev@localhost" }, isAdmin: true, dev: true };
  }
  try {
    const supabase = createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return { user: null, isAdmin: false };

    const allowed = (process.env.ADMIN_EMAILS || "")
      .split(",")
      .map((e) => e.trim().toLowerCase())
      .filter(Boolean);
    if (user.email && allowed.includes(user.email.toLowerCase())) {
      return { user, isAdmin: true };
    }

    const { data: profile } = await supabase
      .from("profiles")
      .select("is_admin")
      .eq("id", user.id)
      .single();
    return { user, isAdmin: !!profile?.is_admin };
  } catch {
    return { user: null, isAdmin: false };
  }
}
