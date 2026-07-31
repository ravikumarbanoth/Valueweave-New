/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
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
module.exports = nextConfig;
