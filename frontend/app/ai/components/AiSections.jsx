const SECTIONS = [
  "AI District Advisor",
  "AI Manufacturing Advisor",
  "AI Readiness Advisor",
  "AI Scale Advisor",
];

export default function AiSections() {
  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {SECTIONS.map((title) => (
        <div key={title} className="card-base p-5 min-h-[150px]">
          <span className="chip bg-violet-50 text-violet-700 border border-violet-100 mb-3">AI-FIRST</span>
          <h2 className="font-display font-bold text-base text-ink mb-2">{title}</h2>
          <p className="text-sm text-muted leading-relaxed">Reserved expansion point for future AI intelligence. No AI logic is active here.</p>
        </div>
      ))}
    </div>
  );
}
