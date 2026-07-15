const SECTIONS = [
  "Automation",
  "Robotics",
  "ERP",
  "Quality",
  "Export",
  "Logistics",
  "Energy",
  "Industrial Resources",
];

export default function ScaleSections() {
  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {SECTIONS.map((title) => (
        <div key={title} className="card-base p-5 min-h-[150px]">
          <span className="chip bg-blue-50 text-blue-700 border border-blue-100 mb-3">SCALE</span>
          <h2 className="font-display font-bold text-base text-ink mb-2">{title}</h2>
          <p className="text-sm text-muted leading-relaxed">Planned scaling layer for mature businesses and industrial operators.</p>
        </div>
      ))}
    </div>
  );
}
