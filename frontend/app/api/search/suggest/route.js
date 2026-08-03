// Live suggestions. The only HTTP endpoint this frontend has, and it earns it.
//
// WHY A ROUTE AND NOT A CLIENT-SIDE INDEX
// ---------------------------------------
// Ranking in memory is what makes this search feel instant, and the memory it
// runs in has to be the server's. The index is ~660 documents; shipping it to
// the browser would put 80 KB and a parse on every visitor including the ones
// who never touch the box, and the research half of it cannot be shipped at
// all — lib/mdx.js reads the filesystem.
//
// So the client sends two characters and gets back eight rows. The payload is
// under 2 KB, the index is already in memory from the last request, and the
// work between them is a scan of 660 short strings.
//
// WHY NOT A SERVER ACTION
// -----------------------
// A GET is cacheable, curl-able and debuggable from a phone browser's address
// bar. A server action is none of those, and the first thing anyone will want
// to know when suggestions look wrong is what the server actually returned.

import { NextResponse } from "next/server";
import { suggest, MIN_QUERY } from "@/lib/search/universal.js";
import { boostFor, isAudience } from "@/lib/journey";

//: Everything the answer depends on is in the URL — the query and, since
//: Phase 9, the audience — so two people typing "elec" as a student in the
//: same minute still cost one computation, and a farmer typing the same thing
//: gets their own entry rather than the student's order. Short, because a
//: package release should show up in the box quickly, and s-maxage rather than
//: max-age so a browser back-button never shows a stale list.
const CACHE = "public, s-maxage=60, stale-while-revalidate=300";

//: Longer than any real query and short enough that the ranker cannot be made
//: to do unbounded work by a long URL.
const MAX_QUERY = 80;

// ─── Rate limiting ──────────────────────────────────────────────────────────
//
// This is the only public API surface the frontend has, and every request
// scans ~660 documents. That is cheap once and not cheap ten thousand times a
// second from one address, and there was no limit anywhere in the repository.
//
// In-process and deliberately simple. A shared store would be correct across
// instances and would need Redis, a schema or a Supabase round trip per
// keystroke — which would cost more than the abuse it prevents. Per instance
// is enough to stop a script; a distributed attack needs a CDN or a WAF and
// this is not the layer for it. Documented in docs/OPERATIONS.md §8 rather
// than left as a surprise.
//
// The limit is generous against real use: the box debounces at 140ms, so a
// fast typist makes about seven requests in ten seconds and this allows sixty.
const WINDOW_MS = 10_000;
const MAX_PER_WINDOW = 60;

//: address -> [windowStartedAt, count]. Swept lazily on write so an idle
//: process does not hold a map of every visitor it has ever seen.
const buckets = new Map();
let sweptAt = 0;

function allowed(address) {
  const now = Date.now();

  if (now - sweptAt > WINDOW_MS) {
    for (const [key, [startedAt]] of buckets) {
      if (now - startedAt > WINDOW_MS) buckets.delete(key);
    }
    sweptAt = now;
  }

  const bucket = buckets.get(address);
  if (!bucket || now - bucket[0] > WINDOW_MS) {
    buckets.set(address, [now, 1]);
    return true;
  }
  bucket[1] += 1;
  return bucket[1] <= MAX_PER_WINDOW;
}

function callerAddress(request) {
  // Behind a proxy the socket address is the proxy's. The first hop in
  // `x-forwarded-for` is the client as the edge saw it — spoofable in general,
  // and good enough here because the consequence of being wrong is one visitor
  // sharing a bucket with another, not a security decision.
  const forwarded = request.headers.get("x-forwarded-for");
  return (forwarded ? forwarded.split(",")[0] : "").trim()
    || request.headers.get("x-real-ip")
    || "unknown";
}

export async function GET(request) {
  const raw = request.nextUrl.searchParams.get("q") || "";
  const q = raw.slice(0, MAX_QUERY).trim();

  if (!allowed(callerAddress(request))) {
    // Empty rather than an error body, and 429 rather than 200: the box treats
    // a failed request as "leave what is on screen", so a limited visitor sees
    // their last suggestions and a working Search button rather than an error.
    return NextResponse.json({ query: q, resolved: null, items: [] }, {
      status: 429,
      headers: { "Retry-After": String(WINDOW_MS / 1000), "Cache-Control": "no-store" },
    });
  }

  if (q.length < MIN_QUERY) {
    // Not an error. Someone typed one letter; they are still going.
    return NextResponse.json({ query: q, resolved: null, items: [] },
                             { headers: { "Cache-Control": CACHE } });
  }

  // Phase 9. An unknown, absent or malformed `as` yields no boost at all, so
  // a hand-typed URL cannot reweight anything and the anonymous path stays
  // byte-identical to what it returned before this parameter existed.
  const as = request.nextUrl.searchParams.get("as");
  const boost = isAudience(as) ? boostFor(as) : undefined;

  try {
    const payload = await suggest(q, { boost });
    return NextResponse.json(payload, { headers: { "Cache-Control": CACHE } });
  } catch {
    // The same contract as every read in lib/knowledge.js: empty, never a
    // stack trace and never a 500. A search box that errors while you type is
    // worse than one that finds nothing, because it is the only signal the
    // reader gets and it says the site is broken.
    return NextResponse.json({ query: q, resolved: null, items: [] },
                             { status: 200, headers: { "Cache-Control": "no-store" } });
  }
}
