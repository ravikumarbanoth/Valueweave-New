import { getPlatformSettings, setting } from "@/lib/settings";

function safeHex(value, fallback) {
  const text = String(value || "").trim();
  return /^#[0-9a-f]{6}$/i.test(text) ? text : fallback;
}

export default async function ThemeStyle() {
  const settings = await getPlatformSettings();
  const primary = safeHex(setting(settings, "theme.primary_color"), "#f59e0b");
  const secondary = safeHex(setting(settings, "theme.secondary_color"), "#14b8a6");
  const accent = safeHex(setting(settings, "theme.accent_color"), "#facc15");

  return (
    <style
      id="platform-theme"
      dangerouslySetInnerHTML={{
        __html: `:root{--vw-primary:${primary};--vw-secondary:${secondary};--vw-accent:${accent};}.btn-primary{background-color:var(--vw-primary)!important;}.btn-primary:hover{filter:brightness(.94);}.btn-teal{background-color:var(--vw-secondary)!important;}.text-amber-500{color:var(--vw-primary)!important;}.text-teal-500{color:var(--vw-secondary)!important;}.bg-amber-500{background-color:var(--vw-primary)!important;}.bg-teal-500{background-color:var(--vw-secondary)!important;}`,
      }}
    />
  );
}
