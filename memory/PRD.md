# ValueWeave — PRD (Living Document)

## Vision
ValueWeave is a Bharat-first collaboration and opportunity discovery platform — and now a **grassroots startup operating system**. Connect students, freelancers, skilled workers, women entrepreneurs, and tier-2/tier-3 builders to discover ideas, collaborators, and form teams locally.

## Architecture
- **Frontend:** Next.js 14 (App Router) in `/app/frontend`
- **Backend / DB / Auth:** Supabase (Postgres + RLS + Google OAuth)
- **Idea Library:** Static JSON dataset (no DB tables yet) — easy migration later
- **Typography:** Plus Jakarta Sans (display) + Inter (body) via `next/font`
- **Styling:** Tailwind CSS, mobile-first
- **Deployment:** Vercel — production at https://valueweave.in

## Public routes
`/` · `/get-started` · `/signin` · `/explore` · `/ideas` · `/ideas/[slug]` · `/about` · `/privacy` · `/terms` · `/opportunities/[id]` · `/profile/[userId]` · `/auth/callback`

## Protected routes
`/dashboard` · `/onboarding` · `/opportunities/new` · `/profile` (self) · `/connections`

## Implemented modules
1. **Landing** — dual CTAs, trust signals, Why-section, Bharat-balanced floating labels (Hyderabad/Warangal/Vijayawada/Coimbatore), expanded footer.
2. **Auth** — Google OAuth via Supabase, smart-routing (`/signin` for returning users, `/get-started` for new), `/auth/callback` exchange.
3. **Onboarding** — lightweight 6-field profile, 53 Bharat-inclusive skill suggestions, 24 interests.
4. **Dashboard / Feed** — category filter, search, skeleton loaders, profile-completion banner, "Nearby" city-boost ranking.
5. **Post Opportunity** — full form, query-param prefill from Idea Library.
6. **Opportunity Detail** — public-readable, WhatsApp + Copy-link share, anon sign-in CTA, accepted-state trust banner.
7. **Profile** — public-readable for others, editable for self.
8. **Connections** — Sent/Received tabs, soft-green accepted styling, explicit "manual contact sharing" helper.
9. **Explore** — public opportunity feed.
10. **Idea Library** ⭐ NEW — 30 balanced Bharat-grounded business ideas (12 local-physical + 9 hybrid + 6 digital + 3 future), public listing with bucket/sector/district/beginner filters + search, detail pages with Problem/Ideal-for/Investment/Skills/Roles/District/Tags + "Start this in your district →" prefill CTA.
11. **Legal pages** — About / Privacy / Terms via shared `LegalShell`.

## Test pass history
- iteration_1 (initial build): 100%
- iteration_2 (typography + public share + diversified suggestions): 12/12
- iteration_3 (smart auth + trust polish + legal pages): 13/13
- iteration_4 (Bharat-rebalance + trust-first connection UX): 13/13
- iteration_5 (Idea Library MVP v1): 14/14

## Idea Library — v1 dataset (30 ideas, static JSON at `/app/frontend/lib/idea-library.js`)
- **Local Physical (12):** Soil Testing Lab, RO Water Service, Mobile Repair Network, Two-Wheeler Workshop, Tailoring Cluster (Women-led), Pickle & Papad Brand, Solar Installation, Dairy Collection Network, Local Delivery Fleet, CCTV Installation, Tuition Hub, Homemade Tiffin Brand
- **Hybrid Tech+Local (9):** WhatsApp Commerce Setup, Business Digitalization Agency, District Marketplace, Drone Spraying, Cloud Kitchen Brand, AI Content Studio, Event Media Crew, Smart Farm Sensors, Beauty Training Center
- **Pure Digital (6):** UI/UX Agency, SEO/Local Marketing Agency, AI Voice-Over Studio, Mobile App Studio, Edu YouTube Channel, Campus Merch
- **Future (3):** EV Charging Hub, Vermicompost Unit, Drone Mapping for Real Estate

Each idea has 15+ fields including bucket, sector, problem_solved, ideal_for (audience), investment tiers, monthly revenue range, team_roles, skills_needed, district_fit, tags.

## Backlog
### P0 (next session candidates)
- Expand Idea Library to 60–100 ideas (incremental)
- Email OTP fallback (Supabase native)
- Profile picture upload (Supabase Storage)
- Idea bookmarks / "Save for later"
- SEO: SSR /ideas/[slug] + /opportunities/[id] + /profile/[userId]

### P1
- District intelligence dashboard (population, dominant industries, employment gap)
- "Suggested ideas for you" based on profile skills/city
- Government schemes table linked to ideas
- Idea voting / community curation
- Vercel Analytics

### P2
- AI matching engine (skills + city + intent → ideas + collaborators)
- Hindi/Telugu/Marathi i18n
- Trust badges / reputation
- Investor / supplier partner directories
- In-app messaging
