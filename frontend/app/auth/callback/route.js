import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase-server";

// Dynamic on purpose and explicitly: it exchanges a one-time OAuth code from
// the query string for a session cookie, so it can never be cached. Already
// dynamic on Next.js 14 (it reads the request); stated so no default can change it.
export const dynamic = "force-dynamic";

export async function GET(request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  const intent = searchParams.get("intent");

  if (code) {
    const supabase = await createClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (!error) {
      // Check whether profile is complete
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        const { data: profile } = await supabase
          .from("profiles")
          .select("profile_complete, looking_for")
          .eq("id", user.id)
          .single();

        // If we have an intent from query and profile doesn't have one yet, persist it
        if (intent && profile && !profile.looking_for) {
          await supabase.from("profiles").update({ looking_for: intent }).eq("id", user.id);
        }

        if (!profile?.profile_complete) {
          return NextResponse.redirect(`${origin}/onboarding`);
        }
        return NextResponse.redirect(`${origin}/dashboard`);
      }
    }
  }
  return NextResponse.redirect(`${origin}/?auth_error=1`);
}
