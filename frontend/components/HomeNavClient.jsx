"use client";

import Link from "next/link";
import MobileNavMenu from "@/components/MobileNavMenu";
import { useLanguage } from "@/lib/language";

export default function HomeNavClient({ navLinks = [] }) {
  const { t } = useLanguage();

  return (
    <nav className="fixed top-0 inset-x-0 z-50 bg-cream/85 backdrop-blur-md border-b border-stone-200/60">
      <div className="max-w-6xl mx-auto h-16 px-4 sm:px-6 flex items-center justify-between gap-3">
        <Link href="/" className="flex items-center gap-2.5 shrink-0 min-h-[44px]">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500 to-yellow-400 flex items-center justify-center shadow-md shadow-amber-500/30">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 3L4 7.5V16.5L12 21L20 16.5V7.5L12 3Z" stroke="#fff" strokeWidth="2" strokeLinejoin="round"/><path d="M4 7.5L12 12M12 12L20 7.5M12 12V21" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>
          </div>
          <span className="font-display font-extrabold text-lg tracking-tight">Value<span className="text-amber-500">Weave</span></span>
        </Link>

        {/* Desktop nav links */}
        <div className="hidden lg:flex items-center gap-1">
          {navLinks.map((l) => (
            <Link key={l.href} href={l.href} className="text-xs font-display font-semibold text-muted hover:text-ink px-2 py-2 rounded-lg hover:bg-stone-100 transition-colors">
              {t(`nav.${l.label.toLowerCase().replaceAll(" ", "-")}`, l.label)}
            </Link>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <Link href="/signin" data-testid="nav-signin" className="btn-secondary !py-2 !px-4 text-sm hidden sm:inline-flex">
            {t("nav.signin", "Sign in")}
          </Link>
          <Link href="/get-started" data-testid="nav-join" className="btn-primary !py-2 !px-4 sm:!px-5 text-sm">
            <span className="sm:hidden">{t("nav.join_short", "Join")}</span>
            <span className="hidden sm:inline">{t("nav.join_full", "Join ValueWeave")}</span>
          </Link>

          {/* Mobile hamburger */}
          <MobileNavMenu />
        </div>
      </div>
    </nav>
  );
}
