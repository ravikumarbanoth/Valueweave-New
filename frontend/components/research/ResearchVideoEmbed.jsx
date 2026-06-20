import { getYouTubeEmbedUrl } from "@/lib/youtube";

export default function ResearchVideoEmbed({ url, title, description }) {
  const embedUrl = getYouTubeEmbedUrl(url);
  if (!embedUrl) return null;

  return (
    <section className="mb-8" data-testid="research-video" data-video-provider="youtube">
      <div className="card-base overflow-hidden bg-white">
        <div className="aspect-video bg-ink">
          <iframe
            src={embedUrl}
            title={title || "ValueWeave research video"}
            loading="lazy"
            className="w-full h-full"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowFullScreen
          />
        </div>
        {(title || description) && (
          <div className="p-4">
            {title && <h2 className="font-display font-bold text-base text-ink">{title}</h2>}
            {description && <p className="text-sm text-muted mt-1 leading-relaxed">{description}</p>}
          </div>
        )}
      </div>
    </section>
  );
}
