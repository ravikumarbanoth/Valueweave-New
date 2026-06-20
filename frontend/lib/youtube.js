export function getYouTubeId(url) {
  if (!url) return "";
  try {
    const value = String(url).trim();
    const parsed = new URL(value);
    if (parsed.hostname.includes("youtu.be")) return parsed.pathname.replace("/", "").split("?")[0];
    if (parsed.searchParams.get("v")) return parsed.searchParams.get("v");
    const embedMatch = parsed.pathname.match(/\/embed\/([^/?]+)/);
    if (embedMatch) return embedMatch[1];
    const shortsMatch = parsed.pathname.match(/\/shorts\/([^/?]+)/);
    if (shortsMatch) return shortsMatch[1];
  } catch {
    const match = String(url).match(/[A-Za-z0-9_-]{11}/);
    return match ? match[0] : "";
  }
  return "";
}

export function getYouTubeEmbedUrl(url) {
  const id = getYouTubeId(url);
  return id ? `https://www.youtube-nocookie.com/embed/${id}` : "";
}

export function isValidYouTubeUrl(url) {
  return !!getYouTubeId(url);
}
