// OpenNext adapter configuration for building ValueWeave for Cloudflare Workers.
//
// Phase 2A (compatibility only): deliberately the adapter's defaults and
// nothing else. The official template adds an R2 incremental cache; R2 is a
// billable service and caching is a later, separately approved phase. With no
// cache configured, OpenNext renders pages on request instead of serving them
// from a cache — correct, just not yet optimised. Vercel does not read this
// file; it only affects `npm run cf:build` / `npm run cf:preview`.
import { defineCloudflareConfig } from "@opennextjs/cloudflare";

export default defineCloudflareConfig();
