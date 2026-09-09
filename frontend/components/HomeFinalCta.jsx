"use client";

import Link from "next/link";
import { useLanguage } from "@/lib/language";

export default function HomeFinalCta() {
  const { t } = useLanguage();

  return (
    <section className="bg-ink text-white py-20 sm:py-24 px-4 sm:px-6 relative overflow-hidden">
      <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-amber-500/20 blur-3xl" />
      <div className="absolute -bottom-20 -left-20 w-96 h-96 rounded-full bg-teal-500/20 blur-3xl" />
      <div className="max-w-3xl mx-auto text-center relative">
        <span className="chip bg-amber-500/20 text-amber-300 border border-amber-500/30 mb-5">
          {t("home.ready_chip", "READY?")}
        </span>
        <h2 className="font-display font-extrabold text-4xl sm:text-5xl md:text-6xl tracking-tight leading-[1.05] mb-5">
          {t("home.step_heading_1", "Take the first step")}<br />
          <span className="bg-gradient-to-r from-amber-500 via-yellow-400 to-teal-500 bg-clip-text text-transparent">
            {t("home.step_heading_2", "from where you are.")}
          </span>
        </h2>
        <p className="text-white/60 text-base sm:text-lg mb-9 leading-relaxed">
          {t("home.step_subheading", "Free. Sign in with Google — no password to remember.")}
        </p>
        <div className="flex items-center justify-center gap-3 flex-wrap">
          <Link href="/get-started" data-testid="footer-cta-join" className="btn-primary !px-7 !py-3.5 text-base">
            {t("home.join_sparkle", "Join ValueWeave ✨")}
          </Link>
          <Link href="/signin" data-testid="footer-cta-signin" className="inline-flex items-center justify-center gap-2 bg-white/10 hover:bg-white/15 border border-white/20 text-white rounded-full px-7 py-3.5 font-display font-semibold text-base transition-colors min-h-[44px]">
            {t("nav.signin", "Sign in")}
          </Link>
        </div>
      </div>
    </section>
  );
}
