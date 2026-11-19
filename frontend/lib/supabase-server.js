import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

// Async since Next.js 15, where cookies() returns a Promise. Every caller
// awaits it: `const sb = await createClient();`. The cookie handling itself is
// unchanged — same getAll/setAll, same silent no-op on set from a Server
// Component.
export async function createClient() {
  const cookieStore = await cookies();
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL || "https://placeholder.supabase.co",
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "placeholder-anon-key",
    {
      cookies: {
        getAll() { return cookieStore.getAll(); },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) => cookieStore.set(name, value, options));
          } catch { /* server component context */ }
        },
      },
    }
  );
}
