const SECTIONS = [
  "Product Discovery",
  "Manufacturing Guides",
  "Factory Planning",
  "Machinery",
  "Raw Materials",
  "Suppliers",
  "Production",
  "Compliance",
];

export default function ManufacturingSections() {
  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {SECTIONS.map((title) => (
        <div key={title} className="card-base p-5 min-h-[150px]">
          <span className="chip bg-amber-50 text-amber-700 border border-amber-100 mb-3">MANUFACTURING</span>
          <h2 className="font-display font-bold text-base text-ink mb-2">{title}</h2>
          <p className="text-sm text-muted leading-relaxed">Planned workspace for manufacturing knowledge, suppliers, setup, and compliance.</p>
        </div>
      ))}
    </div>
  );
}
