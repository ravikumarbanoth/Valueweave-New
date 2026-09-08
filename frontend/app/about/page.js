import LegalShell from "@/components/LegalShell";

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

      <div className="mt-10 pt-8 border-t border-stone-200" data-testid="about-founder">
        <h2 className="font-display font-bold text-xl sm:text-2xl text-ink mb-1">
          Ravi Kumar Banoth
        </h2>
        <p className="text-sm font-display font-semibold text-amber-600 mb-4">
          Founder, ValueWeave
        </p>
        <p className="text-base text-ink leading-relaxed">
          ValueWeave was founded by Ravi Kumar Banoth with a vision to make information about careers, skills, businesses, government schemes, industries and local opportunities easier to discover and act upon.
        </p>
      </div>
    </LegalShell>
  );
}
