import ModuleDashboard from "@/components/platform/ModuleDashboard";

const cards = [
  { emoji: "🧭", title: "Skill Assessment", description: "Map current ability against the capabilities needed to start or join industrial work." },
  { emoji: "🛤️", title: "Learning Paths", description: "Future guided paths for students, founders, operators, and local service providers." },
  { emoji: "🎓", title: "Training", description: "Planned discovery for courses, certifications, internships, and apprenticeships." },
  { emoji: "🤝", title: "Mentors", description: "Future mentor matching for practical readiness and confidence before execution." },
];

export default function ReadinessSections() {
  return (
    <ModuleDashboard
      primaryHref="/readiness"
      primaryLabel="Start Learning"
      roadmap={[
        "Define readiness profiles for founders, students, operators, and local business owners.",
        "Map skills to industries, opportunities, training providers, and district demand.",
        "Introduce guided learning paths once trusted content and partners are available.",
      ]}
      capabilities={["Skill Assessment", "Learning Paths", "Training", "Certifications", "Internships", "Apprenticeships", "Industrial Visits", "Mentors"]}
      cards={cards}
    />
  );
}
