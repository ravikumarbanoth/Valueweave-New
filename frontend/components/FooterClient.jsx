"use client";
import Link from "next/link";
import SocialLinks from "@/components/SocialLinks";
import FooterFounder from "@/components/FooterFounder";
import { useLanguage } from "@/lib/language";

export default function FooterClient({ footerText, contactEmail, footerLinks }) {
  const { t } = useLanguage();

  const getLinkLabel = (link) => {
    const keyMap = {
      "/about": "nav.about",
      "/readiness": "nav.industrial-readiness",
      "/manufacturing": "nav.manufacturing",
      "/scale": "nav.scale",
      "/network": "nav.network",
      "/ai": "nav.ai",
      "/privacy": "nav.privacy",
      "/terms": "nav.terms",
      "/ideas": "nav.ideas",
      "/research": "nav.research",
      "/district": "nav.districts",
      "/districts": "nav.districts",
      "/opportunity-radar": "nav.opportunity-radar",
      "/collaborators": "nav.collaborators",
    };
    const key = keyMap[link.href];
    return key ? t(key, link.label) : link.label;
  };

  return (
    <footer className="border-t border-stone-200 bg-cream" data-testid="site-footer">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-8">
          <div className="max-w-sm">
            <Link href="/" className="flex items-center gap-2.5 mb-3 min-h-[44px] py-1">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500 to-yellow-400 flex items-center justify-center shadow-md shadow-amber-500/30">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 3L4 7.5V16.5L12 21L20 16.5V7.5L12 3Z" stroke="#fff" strokeWidth="2" strokeLinejoin="round"/><path d="M4 7.5L12 12M12 12L20 7.5M12 12V21" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>
              </div>
              <span className="font-display font-extrabold text-lg tracking-tight">Value<span className="text-amber-500">Weave</span></span>
            </Link>
            <p className="text-sm text-muted leading-relaxed">{t("footer.tagline", footerText)}</p>
            {/* Founded by Ravi Kumar Banoth */}
            <p className="text-xs text-stone-500 mt-2 font-medium" data-testid="footer-founder">
              <FooterFounder />
            </p>
          </div>

          <div className="grid sm:grid-cols-2 gap-8 md:gap-12">
            <div>
              <h3 className="font-display font-bold text-sm text-ink mb-3">ValueWeave</h3>
              <div className="flex flex-wrap gap-x-1 gap-y-0.5 text-xs text-muted -mx-2">
                {footerLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="inline-flex items-center min-h-[44px] px-2 rounded-lg
                               hover:text-ink hover:bg-stone-100 font-display font-semibold
                               transition-colors"
                  >
                    {getLinkLabel(link)}
                  </Link>
                ))}
                <a
                  href={`mailto:${contactEmail}`}
                  data-testid="footer-contact"
                  className="inline-flex items-center min-h-[44px] px-2 rounded-lg
                             hover:text-ink hover:bg-stone-100 font-display font-semibold
                             transition-colors"
                >
                  {t("footer.contact", "Contact")}
                </a>
              </div>
            </div>

            <div>
              <h3 className="font-display font-bold text-sm text-ink mb-1">{t("footer.follow_title", "Follow ValueWeave")}</h3>
              <p className="text-xs text-muted mb-3 max-w-xs">{t("footer.follow_desc", "Follow the journey of Bharat's next builders.")}</p>
              <SocialLinks variant="icon" />
            </div>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-stone-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 sm:gap-3 text-xs text-muted">
          <span className="py-2">© {new Date().getFullYear()} ValueWeave. {t("footer.built_in_bharat", "Built in Bharat.")}</span>
          <a
            href={`mailto:${contactEmail}`}
            className="inline-flex items-center min-h-[44px] hover:text-ink font-display font-semibold"
          >
            {contactEmail}
          </a>
        </div>
      </div>
    </footer>
  );
}
