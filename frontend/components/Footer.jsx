import Link from "next/link";
import SocialLinks from "@/components/SocialLinks";
import { getPlatformSettings, setting } from "@/lib/settings";

const FALLBACK_LINKS = [
  { href: "/about", label: "About" },
  { href: "/ideas", label: "Idea Library" },
  { href: "/research", label: "Research" },
  { href: "/district", label: "Districts" },
  { href: "/opportunity-radar", label: "Opportunity Radar" },
  { href: "/collaborators", label: "Collaborators" },
  { href: "/privacy", label: "Privacy" },
  { href: "/terms", label: "Terms" },
];

function safeLinks(value) {
  return Array.isArray(value) && value.length > 0 ? value.filter((l) => l.href && l.label) : FALLBACK_LINKS;
}

export default async function Footer() {
  const settings = await getPlatformSettings();
  const footerText = setting(settings, "footer.text");
  const contactEmail = setting(settings, "footer.contact_email") || setting(settings, "contact.email");
  const footerLinks = safeLinks(setting(settings, "footer.links"));

  return (
    <footer className="border-t border-stone-200 bg-cream" data-testid="site-footer">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-8">
          <div className="max-w-sm">
            {/* PX Phase 10: measured 358x36 — wide but 8px short of the 44px
                tap minimum, same as every other link in this footer. */}
            <Link href="/" className="flex items-center gap-2.5 mb-3 min-h-[44px] py-1">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500 to-yellow-400 flex items-center justify-center shadow-md shadow-amber-500/30">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 3L4 7.5V16.5L12 21L20 16.5V7.5L12 3Z" stroke="#fff" strokeWidth="2" strokeLinejoin="round"/><path d="M4 7.5L12 12M12 12L20 7.5M12 12V21" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>
              </div>
              <span className="font-display font-extrabold text-lg tracking-tight">Value<span className="text-amber-500">Weave</span></span>
            </Link>
            <p className="text-sm text-muted leading-relaxed">{footerText}</p>
          </div>

          <div className="grid sm:grid-cols-2 gap-8 md:gap-12">
            <div>
              <h3 className="font-display font-bold text-sm text-ink mb-3">ValueWeave</h3>
              {/* PX PHASE 10 — TAP TARGETS
                  Measured at 390px: every link here was 16px tall. "About"
                  was 35x16. WCAG 2.5.5 and every mobile platform guideline
                  ask for 44px, and this footer is on all 28 public pages, so
                  it was the most-repeated mobile defect on the site.

                  Fixed with padding and `inline-flex items-center` rather
                  than a bigger font: the text stays the size the design
                  intends and only the touchable box grows. `-mx-2` pulls the
                  new padding back out so the row still lines up with the
                  heading above it. */}
              <div className="flex flex-wrap gap-x-1 gap-y-0.5 text-xs text-muted -mx-2">
                {footerLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="inline-flex items-center min-h-[44px] px-2 rounded-lg
                               hover:text-ink hover:bg-stone-100 font-display font-semibold
                               transition-colors"
                  >
                    {link.label}
                  </Link>
                ))}
                <a
                  href={`mailto:${contactEmail}`}
                  data-testid="footer-contact"
                  className="inline-flex items-center min-h-[44px] px-2 rounded-lg
                             hover:text-ink hover:bg-stone-100 font-display font-semibold
                             transition-colors"
                >
                  Contact
                </a>
              </div>
            </div>

            <div>
              <h3 className="font-display font-bold text-sm text-ink mb-1">Follow ValueWeave</h3>
              <p className="text-xs text-muted mb-3 max-w-xs">Follow the journey of Bharat&apos;s next builders.</p>
              <SocialLinks variant="icon" />
            </div>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-stone-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 sm:gap-3 text-xs text-muted">
          <span className="py-2">© {new Date().getFullYear()} ValueWeave. Built in Bharat.</span>
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
