import AdminShell from "@/components/admin/AdminShell";
import AdminQuickAccess from "@/components/admin/AdminQuickAccess";
import { Zap } from "lucide-react";

export const metadata = {
  title: "Admin Command Center | ValueWeave Admin",
  robots: { index: false, follow: false },
};

export default function AdminToolsPage() {
  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-6">

        <div>
          <span className="chip bg-amber-100 text-amber-700 border border-amber-200">COMMAND CENTER</span>
          <h1 className="font-display font-extrabold text-2xl text-ink mt-2 flex items-center gap-2">
            <Zap size={22} className="text-amber-500" />
            Admin Tools
          </h1>
          <p className="text-stone-500 text-sm mt-1">
            Every admin tool in one place — no more remembering URLs
          </p>
        </div>

        <AdminQuickAccess currentPath="/admin/tools" />

      </div>
    </AdminShell>
  );
}
