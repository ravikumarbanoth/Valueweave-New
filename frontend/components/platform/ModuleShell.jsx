import AppNavbar from "@/components/AppNavbar";

export default function ModuleShell({ badge, title, description, children }) {
  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <main>
        <section className="relative overflow-hidden bg-ink px-4 sm:px-6 py-14">
          <div className="absolute -top-24 -right-24 w-80 h-80 rounded-full bg-amber-500/20 blur-3xl" />
          <div className="absolute -bottom-24 -left-24 w-96 h-96 rounded-full bg-teal-500/20 blur-3xl" />
          <div className="relative max-w-4xl mx-auto text-center">
            <span className="chip bg-amber-500/20 text-amber-300 border border-amber-500/30 mb-4">{badge}</span>
            <h1 className="font-display font-extrabold tracking-tight text-3xl sm:text-4xl md:text-5xl text-white leading-tight mb-4">
              {title}
            </h1>
            <p className="text-white/65 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
              {description}
            </p>
          </div>
        </section>
        <section className="max-w-6xl mx-auto px-4 sm:px-6 py-12 pb-20">
          {children}
        </section>
      </main>
    </div>
  );
}
