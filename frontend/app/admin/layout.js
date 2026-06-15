// Auth gate for ALL /admin/* routes.
// Middleware already requires a session; this additionally enforces is_admin.
// The research sub-layout (/admin/research/layout.js) runs after this and
// renders its own AppNavbar — so this layout returns children without wrapping.

import { redirect } from "next/navigation";
import { getAdminStatus } from "@/lib/admin";

export const dynamic = "force-dynamic";

export default async function AdminLayout({ children }) {
  const { user, isAdmin } = await getAdminStatus();

  if (!user) redirect("/signin");

  if (!isAdmin) {
    // Import lazily to avoid AppNavbar in this server component tree
    const { default: Link } = await import("next/link");
    return (
      <div className="min-h-screen bg-[#FFFBF5] font-body flex items-center justify-center">
        <div className="max-w-sm w-full mx-4 text-center">
          <div className="text-5xl mb-4">🚫</div>
          <span className="chip bg-red-50 text-red-600 border border-red-200 mb-4">403 · FORBIDDEN</span>
          <h1 className="font-display font-extrabold text-2xl mt-3 mb-2 text-[#1C1917]">Admin access required</h1>
          <p className="text-stone-500 text-sm mb-6">
            Your account ({user.email}) does not have admin permissions.
          </p>
          <Link href="/dashboard" className="btn-secondary">Back to dashboard</Link>
        </div>
      </div>
    );
  }

  return children;
}
