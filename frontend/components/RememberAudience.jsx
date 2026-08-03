// Records that this visitor opened an audience's start page. Renders nothing.
//
// WHY A COMPONENT AND NOT A CLICK HANDLER ON THE CHIP
// ---------------------------------------------------
// The homepage chip is one way in. The others are a shared link, a bookmark, a
// search engine, and the "Not quite you?" row at the bottom of another start
// page — and a handler on the chip would miss every one of them. Recording on
// arrival catches all of them, and it is the arrival that means something
// anyway: you are reading the student page, so student is the useful guess.
//
// `/start/[audience]` is a static server component and worth keeping that way,
// so the memory arrives as this: a client island with no markup, no state and
// no effect on what renders.
"use client";

import { useEffect } from "react";
import { remember } from "@/lib/journey";

export default function RememberAudience({ slug }) {
  useEffect(() => {
    remember(slug);
  }, [slug]);
  return null;
}
