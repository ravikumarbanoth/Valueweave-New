"use client";
import Link from "next/link";
import CollaboratorCard from "@/components/CollaboratorCard";
import { MARKETPLACE_SECTORS } from "@/lib/collab";
import { useLanguage } from "@/lib/language";

export default function CollaboratorsClient({ collaborators }) {
  const { t } = useLanguage();

  return (
    <main className="pb-16">
      <section className="relative overflow-hidden bg-ink px-4 sm:px-6 py-14">
        <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-amber-500/20 blur-3xl" />
        <div className="absolute -bottom-20 -left-20 w-96 h-96 rounded-full bg-teal-500/20 blur-3xl" />
        <div className="relative max-w-4xl mx-auto text-center">
          <span className="chip bg-amber-500/20 text-amber-300 border border-amber-500/30 mb-4">{t("collab.badge", "COLLABORATOR MARKETPLACE")}</span>
          <h1 data-testid="collaborators-title" className="font-display font-extrabold tracking-tight text-3xl sm:text-4xl md:text-5xl text-white leading-tight mb-4">
            {t("collab.title", "Find Your Co-Builder")}
          </h1>
          <p className="text-white/60 text-base sm:text-lg max-w-xl mx-auto">
            {t("collab.subtitle", "Builders, innovators, and operators across Telangana and Andhra Pradesh — profiled by the Discover Yourself assessment.")}
          </p>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
        <div className="flex flex-wrap gap-2 mb-8">
          <span className="chip bg-ink text-white">{t("collab.all_sectors", "🌐 All sectors")}</span>
          {MARKETPLACE_SECTORS.map((s) => (
            <Link key={s.id} href={`/collaborators/${s.id}`} className="chip bg-stone-100 text-stone-600 hover:bg-stone-200 transition-colors">
              {s.emoji} {s.label}
            </Link>
          ))}
        </div>

        {collaborators.length === 0 ? (
          <div className="card-base !border-dashed !border-2 p-12 text-center">
            <div className="text-5xl mb-3">🧭</div>
            <h3 className="font-display font-bold text-lg mb-2">{t("collab.be_first_title", "Be the first collaborator in your district")}</h3>
            <p className="text-muted text-sm mb-5 max-w-md mx-auto">
              {t("collab.be_first_desc", "Take the 7-minute Discover Yourself assessment to create your collaborator profile — archetype, founder role, sectors, and budget — and get matched with opportunities.")}
            </p>
            <Link href="/discover" className="btn-primary">{t("collab.take_assessment", "🧭 Take the assessment")}</Link>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {collaborators.map((c) => <CollaboratorCard key={c.user_id} collaborator={c} />)}
          </div>
        )}

        <div className="mt-10 bg-gradient-to-r from-amber-50 to-teal-50 border border-amber-200 rounded-2xl p-6 text-center">
          <h3 className="font-display font-bold text-lg mb-1">{t("collab.want_to_appear_title", "Want to appear here?")}</h3>
          <p className="text-sm text-muted mb-4 max-w-md mx-auto">{t("collab.want_to_appear_desc", "Complete the assessment and publish your collaborator profile — opportunities and co-founders will find you.")}</p>
          <div className="flex items-center justify-center gap-2 flex-wrap">
            <Link href="/discover" className="btn-primary">{t("collab.discover_yourself", "🧭 Discover Yourself")}</Link>
            <Link href="/explore" className="btn-secondary">{t("collab.browse_opps", "Browse opportunities")}</Link>
          </div>
        </div>
      </section>
    </main>
  );
}
