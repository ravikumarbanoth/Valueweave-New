import { unstable_cache } from "next/cache";
import { createClient } from "@supabase/supabase-js";
import { DEFAULT_PLATFORM_SETTINGS } from "@/lib/settings-schema";

function anonClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !key) return null;
  return createClient(url, key, { auth: { persistSession: false } });
}

async function fetchSettings() {
  const settings = { ...DEFAULT_PLATFORM_SETTINGS };
  try {
    const supabase = anonClient();
    if (!supabase) return settings;
    const { data, error } = await supabase
      .from("platform_settings")
      .select("key,value")
      .limit(500);
    if (error) return settings;
    for (const row of data || []) {
      settings[row.key] = row.value;
    }
  } catch {
    return settings;
  }
  return settings;
}

export const getPlatformSettings = unstable_cache(fetchSettings, ["platform-settings"], {
  revalidate: 60,
  tags: ["platform-settings"],
});

export async function getSetting(key) {
  const settings = await getPlatformSettings();
  return settings[key];
}

export function setting(settings, key) {
  return settings?.[key] ?? DEFAULT_PLATFORM_SETTINGS[key];
}

export function enabled(settings, key) {
  const value = setting(settings, key);
  return value === true || value === "true";
}
