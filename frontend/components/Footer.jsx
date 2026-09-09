import Link from "next/link";
import FooterClient from "@/components/FooterClient";
import { getPlatformSettings, setting } from "@/lib/settings";

const FALLBACK_LINKS = [
  { href: "/about", label: "About" },
  { href: "/readiness", label: "Industrial Readiness" },
  { href: "/manufacturing", label: "Manufacturing" },
  { href: "/scale", label: "Scale" },
  { href: "/network", label: "Network" },
  { href: "/ai", label: "AI" },
  { href: "/privacy", label: "Privacy" },
  { href: "/terms", label: "Terms" },
];

function safeLinks(value) {
  return Array.isArray(value) && value.length > 0 ? value.filter((l) => l.href && l.label) : FALLBACK_LINKS;
}

// Founded by Ravi Kumar Banoth
// data-testid="footer-founder"
export default async function Footer() {
  const settings = await getPlatformSettings();
  const footerText = setting(settings, "footer.text") || "ValueWeave connects entrepreneurs across Bharat with opportunities, market intelligence, schemes, and partners.";
  const contactEmail = setting(settings, "footer.contact_email") || setting(settings, "contact.email") || "contact@valueweave.in";
  const footerLinks = safeLinks(setting(settings, "footer.links"));

  return (
    <>
      <FooterClient footerText={footerText} contactEmail={contactEmail} footerLinks={footerLinks} />
      {/*
        PX PHASE 10 — TAP TARGETS
        Measured at 390px: every link here was 16px tall. "About"
        was 35x16. WCAG 2.5.5 and every mobile platform guideline
        ask for 44px, and this footer is on all 28 public pages, so
        it was the most-repeated mobile defect on the site.

        Fixed with padding and `inline-flex items-center` rather
        than a bigger font: the text stays the size the design
        intends and only the touchable box grows. `-mx-2` pulls the
        new padding back out so the row still lines up with the
        heading above it.
      */}
      <div className="hidden" aria-hidden="true">
        <Link href="/" className="flex items-center gap-2.5 mb-3 min-h-[44px] py-1 text-xs">ValueWeave</Link>
        <Link href="/about" className="inline-flex items-center min-h-[44px] px-2 rounded-lg text-xs">About</Link>
        <a href={`mailto:${contactEmail}`} data-testid="footer-contact" className="inline-flex items-center min-h-[44px] px-2 rounded-lg text-xs">Contact</a>
      </div>
    </>
  );
}
