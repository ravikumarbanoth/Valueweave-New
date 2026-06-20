import AdminShell from "@/components/admin/AdminShell";
import { getPlatformSettings } from "@/lib/settings";
import DevopsSettingsClient from "./DevopsSettingsClient";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "DevOps Control Center | ValueWeave Admin",
  robots: { index: false, follow: false },
};

export default async function DevopsPage() {
  const settings = await getPlatformSettings();
  return (
    <AdminShell>
      <DevopsSettingsClient initialSettings={settings} />
    </AdminShell>
  );
}
