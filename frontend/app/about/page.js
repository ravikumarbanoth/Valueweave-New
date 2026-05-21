import Link from "next/link";

export const metadata = { title: "About — ValueWeave" };

export default function AboutPage() {
  return (
    <LegalShell title="About ValueWeave">
      <p>
        ValueWeave is a collaboration platform helping ambitious people across India discover co-builders, opportunities, and meaningful startup or business connections.
      </p>
      <p>
        Built for students, professionals, local entrepreneurs, skilled workers, and builders from every part of Bharat — we exist to bridge the gap between skill and opportunity, between ambition and team, and between idea and execution.
      </p>
      <p>
        We are not a job portal. Not a freelance marketplace. Not a social network.
        ValueWeave is a productive collaboration ecosystem where people find each other and build things that matter — in their own towns and on their own terms.
      </p>
    </LegalShell>
  );
}

function LegalShell({ title, children }) {
  return (
    <div className="min-h-screen bg-cream">
      <nav className="border-b border-stone-200 bg-cream/90 backdrop-blur sticky top-0 z-40">
        <div className="max-w-3xl mx-auto h-16 px-4 sm:px-6 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500 to-yellow-400 flex items-center justify-center">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 3L4 7.5V16.5L12 21L20 16.5V7.5L12 3Z" stroke="#fff" strokeWidth="2" strokeLinejoin="round"/><path d="M4 7.5L12 12M12 12L20 7.5M12 12V21" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>
            </div>
            <span className="font-display font-extrabold tracking-tight">Value<span className="text-amber-500">Weave</span></span>
          </Link>
          <Link href="/" className="text-sm text-muted hover:text-ink font-display font-semibold">← Back home</Link>
        </div>
      </nav>
      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-12">
        <h1 className="font-display font-extrabold text-3xl sm:text-4xl tracking-tight mb-6">{title}</h1>
        <div className="prose prose-stone max-w-none [&>p]:text-ink [&>p]:leading-relaxed [&>p]:mb-5 [&>p]:text-base">
          {children}
        </div>
      </main>
    </div>
  );
}

export { LegalShell };
