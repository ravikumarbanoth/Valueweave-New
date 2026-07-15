const CARDS = [
  "District Overview",
  "Industries",
  "Resources",
  "Infrastructure",
  "Skills",
  "Manufacturing Opportunities",
  "Government Schemes",
];

export default function DistrictModuleCards({ districtName = "District" }) {
  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {CARDS.map((title) => (
        <div key={title} className="card-base p-5 min-h-[160px]">
          <span className="chip bg-emerald-50 text-emerald-700 border border-emerald-100 mb-3">DISTRICT</span>
          <h2 className="font-display font-bold text-base text-ink mb-2">{title}</h2>
          <p className="text-sm text-muted leading-relaxed">
            Planned intelligence area for {districtName}. Content will be connected when the district data model is implemented.
          </p>
        </div>
      ))}
    </div>
  );
}
