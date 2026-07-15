const SECTIONS = [
  "Skill Assessment",
  "Learning Path",
  "Courses",
  "Certifications",
  "Internships",
  "Apprenticeships",
  "Industrial Visits",
  "Mentors",
];

export default function ReadinessSections() {
  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {SECTIONS.map((title) => (
        <div key={title} className="card-base p-5 min-h-[150px]">
          <span className="chip bg-teal-50 text-teal-700 border border-teal-100 mb-3">READY</span>
          <h2 className="font-display font-bold text-base text-ink mb-2">{title}</h2>
          <p className="text-sm text-muted leading-relaxed">Planned module area for structured industrial readiness workflows.</p>
        </div>
      ))}
    </div>
  );
}
