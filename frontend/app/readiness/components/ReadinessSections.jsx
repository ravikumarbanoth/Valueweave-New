// Industrial readiness module — Platform v3.0, Step 4.
//
// Three of the four cards on this dashboard were labelled "Coming Soon" while
// Package006_Skills_and_Training sat synced and unreachable: 45 skills, 25
// training providers and 30 certifications, all with provenance and confidence.
// The wiring was the only thing missing.
//
// Mentors stays unavailable, and stays on the page. The brief is explicit that
// mentors, events, startup workspace and team workspace are not to be removed —
// only relabelled — and no package holds a mentor. That is a NO_DATA_SOURCE, not
// a build queue.
import ModuleDashboard from "@/components/platform/ModuleDashboard";
import { typeCounts } from "@/lib/knowledge";

export default async function ReadinessSections() {
  // Returns {} when the projection is not deployed, so every card falls back to
  // its unavailable state rather than linking into an empty schema.
  const counts = await typeCounts();
  const live = (type, href, label, description) =>
    (counts[type] || 0) > 0
      ? { status: "LIVE", href, count: counts[type], description }
      : {
          status: "NOT_AVAILABLE_YET",
          dependency: `We have researched ${label.toLowerCase()} — this section is still being connected. Check back soon.`,
          description,
        };

  const cards = [
    {
      emoji: "🧭",
      title: "Skills",
      ...live(
        "Skill",
        "/knowledge?type=skill",
        "Skills",
        "Researched skills with NSQF level, difficulty, typical duration, demand and automation risk."
      ),
    },
    {
      emoji: "🎓",
      title: "Certifications",
      ...live(
        "Certification",
        "/knowledge?type=certification",
        "Certifications",
        "Certifications linked to the skills they assess and the businesses that ask for them."
      ),
    },
    {
      emoji: "🏫",
      title: "Training providers",
      ...live(
        "TrainingProvider",
        "/knowledge?type=provider",
        "Training providers",
        "Institutions that deliver the training, linked to the skills they teach."
      ),
    },
    {
      emoji: "🤝",
      title: "Mentors",
      description: "Matching a learner to someone who has already done the work.",
      status: "NO_DATA_SOURCE",
      dependency:
        "Mentors are being gathered now. In the meantime you can find people to " +
        "work with in the collaborator marketplace.",
    },
  ];

  return (
    <ModuleDashboard
      primaryHref="/knowledge?type=skill"
      primaryLabel="Browse skills"
      dependency={
        "Skill tests, learning paths, internships and apprenticeships are on the way. " +
        "The skills, certificates and training centres they will string together are " +
        "already researched and open above."
      }
      roadmap={[
        "Work out what being ready looks like for a student, a first-time owner and someone already running a business.",
        "Map skills to industries, opportunities, training providers, and district demand.",
        "Add step-by-step learning paths once we have training partners we trust enough to send you to.",
      ]}
      capabilities={[
        { label: "Skills", status: counts.Skill ? "LIVE" : "NOT_AVAILABLE_YET", href: "/knowledge?type=skill", count: counts.Skill },
        { label: "Certifications", status: counts.Certification ? "LIVE" : "NOT_AVAILABLE_YET", href: "/knowledge?type=certification", count: counts.Certification },
        { label: "Training providers", status: counts.TrainingProvider ? "LIVE" : "NOT_AVAILABLE_YET", href: "/knowledge?type=provider", count: counts.TrainingProvider },
        { label: "Skill assessment", dependency: "We are working out a way to score this that is fair to everyone." },
        { label: "Learning paths", dependency: "We know what each skill needs, but not yet what order to learn them in." },
        { label: "Internships", dependency: "Internship openings are being gathered now." },
        { label: "Apprenticeships", dependency: "Apprenticeship openings are being gathered now." },
        { label: "Mentors", dependency: "Mentors are being gathered now." },
      ]}
      cards={cards}
    />
  );
}
