import Link from "next/link";
import SocialLinks from "@/components/SocialLinks";

const FOOTER_LINKS = [
  { href: "/about", label: "About" },
  { href: "/ideas", label: "Idea Library" },
  { href: "/privacy", label: "Privacy" },
  { href: "/terms", label: "Terms" },
];

export default function Footer() {
  return (
    <footer className="border-t border-stone-200 bg-cream" data-testid="site-footer">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-8">
          <div className="max-w-sm">
            <Link href="/" className="flex items-center gap-2.5 mb-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500 to-yellow-400 flex items-center justify-center shadow-md shadow-amber-500/30">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 3L4 7.5V16.5L12 21L20 16.5V7.5L12 3Z" stroke="#fff" strokeWidth="2" strokeLinejoin="round"/><path d="M4 7.5L12 12M12 12L20 7.5M12 12V21" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>
              </div>
              <span className="font-display font-extrabold text-lg tracking-tight">Value<span className="text-amber-500">Weave</span></span>
            </Link>
            <p className="text-sm text-muted leading-relaxed">
              Where ambition finds its team. Find what to build and who to build it with — from your district.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 gap-8 md:gap-12">
            <div>
              <h3 className="font-display font-bold text-sm text-ink mb-3">ValueWeave</h3>
              <div className="flex flex-wrap gap-x-4 gap-y-2 text-xs text-muted">
                {FOOTER_LINKS.map((link) => (
                  <Link key={link.href} href={link.href} className="hover:text-ink font-display font-semibold">
                    {link.label}
                  </Link>
                ))}
                <a
                  href="mailto:valueweave.team@gmail.com"
                  data-testid="footer-contact"
                  className="hover:text-ink font-display font-semibold"
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

        <div className="mt-8 pt-6 border-t border-stone-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 text-xs text-muted">
          <span>© {new Date().getFullYear()} ValueWeave. Built in Bharat.</span>
          <a href="mailto:valueweave.team@gmail.com" className="hover:text-ink font-display font-semibold">
            valueweave.team@gmail.com
          </a>
        </div>
      </div>
    </footer>
  );
}
