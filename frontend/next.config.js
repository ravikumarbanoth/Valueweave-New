const { execFileSync } = require("node:child_process");
const path = require("node:path");
const { PHASE_PRODUCTION_BUILD, PHASE_DEVELOPMENT_SERVER } = require("next/constants");

// The research-article registry (scripts/build-research-registry.mjs) must
// exist before any build. It is generated HERE rather than only in the npm
// `build` script because the command that runs the build is not always ours:
// Vercel uses package.json's `build` script unless the project overrides it,
// a person may run `next build` directly, and OpenNext runs the build for
// Cloudflare. Every one of those loads this file, so the registry is always
// current. Only in the build and dev phases — `next start` and the deployed
// runtimes never rebuild it.
function buildResearchRegistry() {
  execFileSync(process.execPath, [path.join(__dirname, "scripts", "build-research-registry.mjs")], {
    stdio: "inherit",
  });
}

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Next.js 15 changed the client router cache: a dynamic page visited in the
  // last 30 seconds used to be reused on back/forward and link navigation; in
  // 15 the default is 0, so every navigation refetches it. These are the
  // Next.js 14 values, set explicitly so the upgrade does not change how often
  // the browser asks the server for a page.
  experimental: {
    staleTimes: { dynamic: 30, static: 300 },
  },
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**" },
    ],
  },

  // Legacy URLs.
  //
  // `/explore/<id>` was linked from every featured-opportunity card on the
  // landing page and has never existed as a route — `app/explore/` contains only
  // `page.js`. Every one of those clicks produced a 404. The card now points at
  // `/opportunities/<id>`, and this catches the links already shared, bookmarked
  // or indexed.
  //
  // Permanent (308): the destination is the real home of the page and nothing is
  // planned at the old path.
  //
  // `:id+` and NOT `:id*`. The `*` modifier matches ZERO or more segments, so it
  // also matched `/explore` itself and redirected the working marketplace page to
  // `/opportunities`. Caught by curling the route against a running server — the
  // redirect looked correct in the config and broke a live page. `+` is
  // one-or-more, which is what "a legacy detail URL" actually means, and it still
  // covers the district variant `/explore/<id>/<district>`.
  async redirects() {
    return [
      { source: "/explore/:id+", destination: "/opportunities/:id+", permanent: true },
    ];
  },
};
module.exports = (phase) => {
  if (phase === PHASE_PRODUCTION_BUILD || phase === PHASE_DEVELOPMENT_SERVER) buildResearchRegistry();
  return nextConfig;
};
