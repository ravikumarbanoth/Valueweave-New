"use client";

import Link from "next/link";
import MobileNavMenu from "@/components/MobileNavMenu";
import HeaderActions from "@/components/HeaderActions";
import { useLanguage } from "@/lib/language";

export default function HomeNavClient({ navLinks = [] }) {
  const { t } = useLanguage();

  return (
    <nav className="fixed top-0 inset-x-0 z-50 bg-cream/85 backdrop-blur-md border-b border-stone-200/60">
      {/*
        TWO LAYOUTS, ONE ROW.

        Below lg the arrangement is the one in the reference header: hamburger
        left, logo centred, icon tiles right. The logo is centred by absolute
        positioning rather than by a spacer, because the two sides are
        different widths and a flex centre would drift as the right cluster
        changes.

        From lg the logo returns to the left and the navigation links reappear
        between it and the icons — centring it there would push six links into
        the right half and leave the left empty.
      */}
      {/*
        Same three-column grid as AppNavbar. The landing header was NOT the
        one overlapping — it only ever shows two action tiles, so the old
        absolute centring had room — but leaving one header on absolute
        positioning and the other on a grid would mean the brand shifts as a
        reader moves from the landing page to any other, and the next person
        to add an icon here would reintroduce the same bug. Identical
        structure, and the rendered desktop row is unchanged.
      */}
      <div className="max-w-6xl mx-auto h-16 px-3 sm:px-4 lg:px-6
                      grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-2
                      md:flex md:gap-3">
        <div className="flex items-center shrink-0 lg:hidden">
          <MobileNavMenu />
        </div>

        <Link
          href="/"
          data-testid="home-nav-logo"
          className="flex items-center gap-2.5 min-w-0 min-h-[44px]
                     justify-self-center md:justify-self-start md:shrink-0"
        >
          <div className="w-9 h-9 shrink-0 rounded-xl bg-gradient-to-br from-amber-500 to-yellow-400 flex items-center justify-center shadow-md shadow-amber-500/30">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 3L4 7.5V16.5L12 21L20 16.5V7.5L12 3Z" stroke="#fff" strokeWidth="2" strokeLinejoin="round"/><path d="M4 7.5L12 12M12 12L20 7.5M12 12V21" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>
          </div>
          <span className="truncate font-display font-extrabold text-lg tracking-tight">Value<span className="text-amber-500">Weave</span></span>
        </Link>

        {/* Desktop nav links */}
        <div className="hidden lg:flex items-center gap-1">
          {navLinks.map((l) => (
            <Link key={l.href} href={l.href} className="text-xs font-display font-semibold text-muted hover:text-ink px-2 py-2 rounded-lg hover:bg-stone-100 transition-colors">
              {t(`nav.${l.label.toLowerCase().replaceAll(" ", "-")}`, l.label)}
            </Link>
          ))}
        </div>

        <div className="flex items-center gap-1.5 sm:gap-2 justify-self-end md:ml-auto">
          <HeaderActions />

          {/*
            Sign in and Join are hidden below lg. They are not lost: the
            hamburger drawer already ends with both, so the phone header keeps
            the reference's three-icon shape without removing a route in.
          */}
          <Link href="/signin" data-testid="nav-signin" className="btn-secondary !py-2 !px-4 text-sm hidden lg:inline-flex whitespace-nowrap">
            {t("nav.signin", "Sign in")}
          </Link>
          <Link href="/get-started" data-testid="nav-join" className="btn-primary !py-2 !px-4 sm:!px-5 text-sm hidden lg:inline-flex whitespace-nowrap">
            {t("nav.join_full", "Join ValueWeave")}
          </Link>
        </div>
      </div>
    </nav>
  );
}
