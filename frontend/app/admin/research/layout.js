// Auth gate for all /admin/research/* pages.
// Middleware already requires a session for /admin (redirects to sign-in
// flow); this layout additionally enforces the admin role: signed-in
// non-admins get a 403, signed-out users (edge case) go to /signin.

import Link from "next/link";
import { redirect } from "next/navigation";
import { getAdminStatus } from "@/lib/admin";
import AppNavbar from "@/components/AppNavbar";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Research Admin | ValueWeave",
  robots: { index: false, follow: false },
};

export default async function AdminResearchLayout({ children }) {
  const { user, isAdmin } = await getAdminStatus();

  if (!user) redirect("/signin");

  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-cream font-body">
        <AppNavbar />
        <main className="max-w-md mx-auto px-4 py-24 text-center" data-testid="admin-403">
          <div className="text-6xl mb-4">🚫</div>
          <span className="chip bg-red-50 text-red-600 border border-red-200 mb-4">403 · FORBIDDEN</span>
          <h1 className="font-display font-extrabold text-2xl mb-3">Admin access required</h1>
          <p className="text-muted text-sm leading-relaxed mb-6">
            Your account ({user.email}) doesn&apos;t have publishing permissions.
            Ask a ValueWeave administrator to grant you access.
          </p>
          <Link href="/dashboard" className="btn-secondary">Back to feed</Link>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      {children}
    </div>
  );
}
