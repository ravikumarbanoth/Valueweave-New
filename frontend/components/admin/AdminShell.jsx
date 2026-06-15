import AppNavbar from "@/components/AppNavbar";
import AdminSidebar from "@/components/admin/AdminSidebar";

export default function AdminShell({ children }) {
  return (
    <div className="min-h-screen bg-[#FFFBF5] font-body">
      <AppNavbar />
      <div className="flex">
        <AdminSidebar />
        <main className="flex-1 min-w-0 overflow-x-hidden">{children}</main>
      </div>
    </div>
  );
}
