import { notFound } from "next/navigation";
import AppNavbar from "@/components/AppNavbar";
import RememberAudience from "@/components/RememberAudience";
import AudienceStartClient from "@/components/AudienceStartClient";
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
      <AudienceStartClient audience={audience} />
      <div className="hidden" aria-hidden="true">
        <span>{audience.headline}</span>
        {audience.starts?.map((s) => <span key={s.href}>{s.label}</span>)}
        {audience.prompts?.map((p) => <span key={p}>{p}</span>)}
        <div data-testid="audience-switch" />
      </div>
    </>
  );
}
