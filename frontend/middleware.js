import { createServerClient } from "@supabase/ssr";
import { NextResponse } from "next/server";

// Only these exact paths (or paths starting with them when explicitly listed) require auth.
// Public: /, /get-started, /auth/callback, /opportunities/[id] (shareable), /profile/[userId] (shareable).
function requiresAuth(pathname) {
  if (pathname === "/dashboard" || pathname.startsWith("/dashboard/")) return true;
  if (pathname === "/onboarding") return true;
  if (pathname === "/opportunities/new") return true;
  if (pathname === "/profile") return true; // /profile/[userId] is public
  if (pathname === "/connections" || pathname.startsWith("/connections/")) return true;
  return false;
}

export async function middleware(request) {
  let response = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
    {
      cookies: {
        getAll() { return request.cookies.getAll(); },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
          response = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) => response.cookies.set(name, value, options));
        },
      },
    }
  );

  // Refresh session for all requests so cookies stay valid
  const { data: { user } } = await supabase.auth.getUser();

  if (requiresAuth(request.nextUrl.pathname) && !user) {
    const url = request.nextUrl.clone();
    url.pathname = "/";
    url.searchParams.set("auth", "required");
    return NextResponse.redirect(url);
  }
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)"],
};
