// The curated way in, one page per kind of visitor.
//
// The homepage now asks who you are before it asks anything else. This is what
// each answer opens: the same surfaces the site already had, introduced in the
// order that makes sense for that person, in the second person.
//
// Deliberately thin. It reads no data and adds no route to maintain beyond
// itself — every card is a link into a page that already exists, and the
// counts in the hints come from the built graph rather than from a query, so
// the page renders identically whether or not the projection is reachable.
// A curated start page that shows "0 skills" on a bad day would be worse than
// one that shows nothing at all.
//
// Phase 9 turns the same six into an onboarding flow. This is the routing and
// the copy; that adds the memory.
//
// Phase 9: the memory is `<RememberAudience>` below — a client island with no
// markup, so this page stays static and renders exactly as it did.
import Link from "next/link";
import { notFound } from "next/navigation";
import AppNavbar from "@/components/AppNavbar";
import RememberAudience from "@/components/RememberAudience";
import { AUDIENCES, AUDIENCE_BY_SLUG } from "@/lib/audiences";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";

export function generateStaticParams() {
  return AUDIENCES.map((a) => ({ audience: a.slug }));
}

export function generateMetadata({ params }) {
  const audience = AUDIENCE_BY_SLUG[params.audience];
  if (!audience) return {};
  return buildBaseMetadata({
    title: `For ${audience.label.toLowerCase()}s | ValueWeave`,
    description: audience.intro,
    alternates: { canonical: `${BASE_URL}/start/${audience.slug}` },
  });
}

export default function AudienceStartPage({ params }) {
  const audience = AUDIENCE_BY_SLUG[params.audience];
  if (!audience) notFound();

  return (
    <>
      <RememberAudience slug={audience.slug} />
      <AppNavbar />
      <main className="min-h-screen bg-cream font-body pb-16">
        <section className="bg-ink text-white px-4 sm:px-6 py-12 sm:py-14">
          <div className="max-w-3xl mx-auto">
            <Link href="/" className="inline-flex items-center min-h-[44px] text-xs text-white/50 hover:text-white/80">
              ← Back to home
            </Link>
            <p className="text-4xl mt-4 mb-3" aria-hidden="true">{audience.emoji}</p>
            <h1 className="font-display font-extrabold tracking-tight text-3xl sm:text-4xl leading-tight mb-4">
              {audience.headline}
            </h1>
            <p className="text-white/65 leading-relaxed max-w-2xl">{audience.intro}</p>
          </div>
        </section>

        <section className="max-w-3xl mx-auto px-4 sm:px-6 py-10">
          <h2 className="label-display mb-4">Start with one of these</h2>
          <div className="flex flex-col gap-3" data-testid="audience-starts">
            {audience.starts.map((start, index) => (
              <Link
                key={start.href}
                href={start.href}
                data-testid="audience-start"
                className="card-base p-5 flex items-center gap-4 hover:border-amber-300 hover:shadow-md transition-all group"
              >
                <span className="shrink-0 w-8 h-8 rounded-full bg-amber-50 border border-amber-100 flex items-center justify-center font-display font-bold text-sm text-amber-700 tabular-nums">
                  {index + 1}
                </span>
                <span className="min-w-0">
                  <span className="block font-display font-bold text-ink group-hover:text-amber-700 transition-colors">
                    {start.label}
                  </span>
                  <span className="block text-sm text-muted mt-0.5">{start.hint}</span>
                </span>
                <span className="ml-auto text-amber-700 shrink-0" aria-hidden="true">→</span>
              </Link>
            ))}
          </div>

          <h2 className="label-display mt-10 mb-3">Or search for something specific</h2>
          <div className="flex flex-wrap gap-2" data-testid="audience-prompts">
            {audience.prompts.map((prompt) => (
              <Link
                key={prompt}
                href={`/knowledge?q=${encodeURIComponent(prompt)}`}
                className="chip bg-white text-stone-600 border border-stone-200 hover:border-amber-300 hover:bg-amber-50 transition-colors"
              >
                {prompt}
              </Link>
            ))}
          </div>

          {/* Never a dead end, and never a one-way door: someone who picked the
              wrong chip on the homepage should not have to go back to fix it. */}
          <div className="mt-10 pt-6 border-t border-stone-200">
            <p className="text-sm text-muted mb-3">Not quite you?</p>
            <div className="flex flex-wrap gap-2" data-testid="audience-switch">
              {AUDIENCES.filter((a) => a.slug !== audience.slug).map((other) => (
                <Link
                  key={other.slug}
                  href={`/start/${other.slug}`}
                  className="chip bg-white text-stone-600 border border-stone-200 hover:border-teal-500 hover:bg-teal-50 transition-colors"
                >
                  <span aria-hidden="true" className="mr-1">{other.emoji}</span>
                  {other.label}
                </Link>
              ))}
            </div>
          </div>
        </section>
      </main>
    </>
  );
}
