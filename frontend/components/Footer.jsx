import Link from "next/link";
import SocialLinks from "@/components/SocialLinks";

// Reusable site footer. Drop <Footer /> at the bottom of the landing page (and any
// other public page). Matches the existing cream/amber/ink palette and font-display
// type; no new tokens introduced.
export default function Footer() {
  return (
    <footer className="border-t border-stone-200 bg-cream" data-testid="site-footer">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-8">
          {/* Brand */}
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

          {/* Follow */}
          <div>
            <h3 className="font-display font-bold text-sm text-ink mb-1">Follow ValueWeave</h3>
            <p className="text-xs text-muted mb-3 max-w-xs">Follow the journey of Bharat&apos;s next builders.</p>
            <SocialLinks variant="icon" />
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-stone-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 text-xs text-muted">
          <span>© {new Date().getFullYear()} ValueWeave. Built in Bharat.</span>
          <div className="flex items-center gap-4">
            <Link href="/privacy" className="hover:text-ink font-display font-semibold">Privacy</Link>
            <Link href="/terms" className="hover:text-ink font-display font-semibold">Terms</Link>
            <Link href="/ideas" className="hover:text-ink font-display font-semibold">Idea Library</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
