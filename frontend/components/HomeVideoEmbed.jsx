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
            See how it works in 60 seconds
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
              {/* Step 4: "coming soon" promised a date nobody had set. An
                  explainer video is not knowledge and has no package behind it;
                  it is waiting on someone recording one. */}
              <p className="text-white/60 text-sm">Video coming shortly</p>
              <p className="text-white/40 text-xs max-w-xs text-center leading-relaxed">
                We are putting one together. In the meantime, everything it would
                explain is already on the site.
              </p>
            </div>
          )}
        </div>

        <div className="flex justify-center mt-6">
          <a
            href="https://www.youtube.com/@valueweave"
            target="_blank"
            rel="noopener noreferrer"
            data-testid="home-youtube-link"
            className="inline-flex items-center gap-2 rounded-full border border-stone-200 bg-white px-4 py-2 text-sm font-display font-bold text-ink hover:border-red-300 hover:text-red-600 transition-colors"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.5 12 3.5 12 3.5s-7.5 0-9.4.6A3 3 0 0 0 .5 6.2 31.3 31.3 0 0 0 0 12a31.3 31.3 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.6 9.4.6 9.4.6s7.5 0 9.4-.6a3 3 0 0 0 2.1-2.1A31.3 31.3 0 0 0 24 12a31.3 31.3 0 0 0-.5-5.8ZM9.6 15.6V8.4l6.3 3.6-6.3 3.6Z" />
            </svg>
            More videos on YouTube
          </a>
        </div>
      </div>
    </section>
  );
}
