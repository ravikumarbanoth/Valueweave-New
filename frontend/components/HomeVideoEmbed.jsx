"use client";

export default function HomeVideoEmbed({
  youtubeUrl = "https://youtu.be/hRhhYQLPJ7Q?si=ZPAl8q878ZuNFZkY",
}) {
  const getEmbedId = (url) => {
    try {
      const u = new URL(url);
      if (u.hostname === "youtu.be") return u.pathname.slice(1).split("?")[0];
      return u.searchParams.get("v") || "";
    } catch {
      return "";
    }
  };

  const embedId = getEmbedId(youtubeUrl);
  const embedSrc = embedId
    ? `https://www.youtube-nocookie.com/embed/${embedId}?rel=0&modestbranding=1`
    : null;

  return (
    <section className="py-16 sm:py-20 px-4 sm:px-6 bg-warm">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-10">
          <span className="chip bg-teal-100 text-teal-600 mb-4">🎥 EXPLAINER</span>
          <h2 className="font-display font-extrabold text-3xl sm:text-4xl tracking-tight text-ink mb-3">
            Watch ValueWeave in 60 Seconds
          </h2>
          <p className="text-muted text-base">
            See how ValueWeave helps India&apos;s builders discover, connect and launch.
          </p>
        </div>

        <div className="relative w-full rounded-2xl overflow-hidden shadow-xl border border-stone-200 bg-ink"
          style={{ aspectRatio: "16/9" }}
        >
          {embedSrc ? (
            <iframe
              src={embedSrc}
              title="ValueWeave explainer video"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              loading="lazy"
              className="absolute inset-0 w-full h-full border-0"
            />
          ) : (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-4">
              <div className="w-16 h-16 rounded-full bg-amber-500/20 flex items-center justify-center">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                  <path d="M5 3l14 9-14 9V3z" fill="white" />
                </svg>
              </div>
              <p className="text-white/60 text-sm">Video coming soon</p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
