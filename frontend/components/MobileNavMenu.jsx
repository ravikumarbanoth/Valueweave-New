"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Menu, X } from "lucide-react";
import { createClient } from "@/lib/supabase-browser";
import { NAVIGATION_SETTING_KEYS } from "@/lib/settings-schema";
import { useLanguage } from "@/lib/language";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/discover", label: "Discover", key: NAVIGATION_SETTING_KEYS.discover },
  { href: "/ideas", label: "Idea Library" },
  { href: "/research", label: "Research", key: NAVIGATION_SETTING_KEYS.research },
  { href: "/districts", label: "Districts", key: NAVIGATION_SETTING_KEYS.districts },
  { href: "/opportunity-radar", label: "Opportunity Radar", key: NAVIGATION_SETTING_KEYS.radar },
  { href: "/collaborators", label: "Collaborators", key: NAVIGATION_SETTING_KEYS.collaborators },
];

export default function MobileNavMenu() {
  const [open, setOpen] = useState(false);
  const [navSettings, setNavSettings] = useState({});
  const { t } = useLanguage();

  useEffect(() => {
    createClient()
      .from("platform_settings")
      .select("key,value")
      .in("key", Object.values(NAVIGATION_SETTING_KEYS))
      .then(({ data }) => setNavSettings(Object.fromEntries((data || []).map((row) => [row.key, row.value]))));
  }, []);

  const links = LINKS.filter((link) => !link.key || navSettings[link.key] !== false);

  return (
    <>
      <button
        onClick={() => setOpen((o) => !o)}
        aria-label={open ? "Close menu" : "Open menu"}
        data-testid="mobile-nav-toggle"
        //: Rounded-square amber tile, matching the search / YouTube tiles in
        //: HeaderActions so the three sit as one set rather than one plain
        //: button beside two coloured ones. 44px is unchanged.
        className="lg:hidden w-11 h-11 flex items-center justify-center rounded-2xl bg-amber-50 text-amber-600 hover:bg-amber-100 transition-colors min-h-[44px] min-w-[44px]"
      >
        {open ? <X size={20} aria-hidden="true" /> : <Menu size={20} aria-hidden="true" />}
      </button>

      {open && (
        <div className="fixed inset-0 z-40 bg-ink/30 backdrop-blur-sm lg:hidden" onClick={() => setOpen(false)} />
      )}

      <div className={`lg:hidden fixed top-16 inset-x-0 z-50 bg-white border-b border-stone-200 shadow-xl transition-all duration-200 ${open ? "opacity-100 pointer-events-auto translate-y-0" : "opacity-0 pointer-events-none -translate-y-2"}`}>
        <nav className="px-4 py-3 flex flex-col gap-0.5 max-h-[calc(100vh-5rem)] overflow-y-auto">
          {links.map((l) => (
            <Link key={l.href} href={l.href} onClick={() => setOpen(false)} className="flex items-center px-3 py-3 rounded-xl text-sm font-display font-semibold text-ink hover:bg-amber-50 hover:text-amber-700 transition-colors min-h-[44px]">
              {t(`nav.${l.label.toLowerCase().replaceAll(" ", "-")}`, l.label)}
            </Link>
          ))}
          <div className="border-t border-stone-100 my-2" />
          <Link href="/signin" onClick={() => setOpen(false)} className="btn-secondary w-full justify-center text-sm">{t('nav.signin', 'Sign in')}</Link>
          <Link href="/get-started" onClick={() => setOpen(false)} className="btn-primary w-full justify-center text-sm mt-1">{t('nav.join', 'Join ValueWeave →')}</Link>
        </nav>
      </div>
    </>
  );
}
