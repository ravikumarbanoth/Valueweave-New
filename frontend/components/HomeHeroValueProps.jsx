"use client";

import Link from "next/link";
import { Shield, Smartphone, Sparkles } from "lucide-react";
import { useLanguage } from "@/lib/language";

export default function HomeHeroValueProps({ primaryCta, secondaryCta, tertiaryCta }) {
  const { t } = useLanguage();

  return (
    <>
      <ul className="flex flex-wrap justify-center gap-x-5 gap-y-2 mt-10">
        <li className="inline-flex items-center gap-1.5 text-xs sm:text-sm text-muted">
          <Shield size={14} className="text-teal-600" /> {t("home.google_auth", "Google-authenticated profiles")}
        </li>
        <li className="inline-flex items-center gap-1.5 text-xs sm:text-sm text-muted">
          <Smartphone size={14} className="text-teal-600" /> {t("home.mobile_first", "Mobile-first")}
        </li>
        <li className="inline-flex items-center gap-1.5 text-xs sm:text-sm text-muted">
          <Sparkles size={14} className="text-teal-600" /> {t("home.free_to_join", "Free to join")}
        </li>
      </ul>

      <div className="flex flex-wrap justify-center gap-3 mt-6" data-testid="hero-secondary-ctas">
        <Link href="/discover" data-testid="hero-cta-discover" className="btn-secondary text-sm">
          ⚡ {t("home.cta_discover", primaryCta || "Discover Yourself")}
        </Link>
        <Link href="/ideas" data-testid="hero-cta-ideas" className="btn-secondary text-sm">
          💡 {t("home.cta_ideas", secondaryCta || "Explore Ideas")}
        </Link>
        <Link href="/network" data-testid="hero-cta-collabs" className="btn-secondary text-sm">
          👥 {t("home.cta_network", tertiaryCta || "Find Collaborators")}
        </Link>
      </div>
    </>
  );
}
