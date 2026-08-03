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

//: Nothing in the answer depends on the visitor, so two people typing "elec"
//: in the same minute should cost one computation. Short, because a package
//: release should show up in the box quickly, and s-maxage rather than
//: max-age so a browser back-button never shows a stale list.
const CACHE = "public, s-maxage=60, stale-while-revalidate=300";

//: Longer than any real query and short enough that the ranker cannot be made
//: to do unbounded work by a long URL.
const MAX_QUERY = 80;

export async function GET(request) {
  const raw = request.nextUrl.searchParams.get("q") || "";
  const q = raw.slice(0, MAX_QUERY).trim();

  if (q.length < MIN_QUERY) {
    // Not an error. Someone typed one letter; they are still going.
    return NextResponse.json({ query: q, resolved: null, items: [] },
                             { headers: { "Cache-Control": CACHE } });
  }

  try {
    const payload = await suggest(q);
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
