# ValueWeave — PRD (Living Document)

## Vision
ValueWeave is a collaboration and opportunity discovery platform for India's tier-2/tier-3 builders. Connect students, freelancers, skilled workers, and entrepreneurs to discover collaborators, form startup teams, and create real economic opportunities. Not a job portal, not LinkedIn, not Fiverr — a productive collaboration ecosystem.

## Architecture (final, simple)
- **Frontend:** Next.js 14 (App Router) in `/app/frontend`
- **Backend / DB / Auth:** Supabase (Postgres + RLS + Google OAuth)
- **No separate backend service**
- **Styling:** Tailwind CSS, mobile-first
- **Typography:** Plus Jakarta Sans (display) + Inter (body) via next/font
- **Deployment:** Vercel — production at https://valueweave.in

## Users
Students · Unemployed youth · AI learners · Local entrepreneurs · Skilled workers · Freelancers · Startup builders · Tier-2/3 opportunity seekers

## Implemented (v1 — 2026-01)
### Core flows
- Landing page (hero, how-it-works, categories, final CTA, footer) — "29 states" copy
- Get Started intent selection (8 cards) → Google OAuth via Supabase
- `/auth/callback` route exchanges code → routes to `/onboarding` or `/dashboard`
- Lightweight Onboarding (name, city, skills, interests, looking_for, bio)
- Dashboard / Feed with category filter (8) + keyword search + skeleton loader + profile completion banner
- Post Opportunity
- **Public** Opportunity Detail (`/opportunities/[id]`) with WhatsApp + Copy-link Share, anon sign-in CTA
- **Public** User Profile (`/profile/[userId]`) with Share buttons + anon "Join" CTA
- My Profile (`/profile`) — editable via re-onboarding
- Connections — Sent/Received tabs, accept/decline

### Polish & infra
- Auth-aware AppNavbar (anon shows Sign-in/Join, authed shows Feed/Post/Inbox/Profile + bottom mobile nav with safe-area inset)
- Logo always navigates home (`/` for anon, `/dashboard` for authed)
- All URLs dynamic via `window.location.origin` and request origin — no localhost/vercel.app hardcodes
- `metadataBase: https://valueweave.in` for OG tags
- 44px min touch targets, `pb-[max(0.375rem,env(safe-area-inset-bottom))]` on mobile nav
- Skeleton loaders (FeedSkeleton)
- Diversified skill (35) + interest (23) suggestions covering local-business, trades, Bharat-ecosystem
- Supabase schema in `supabase_schema.sql` with RLS (public read, owner-write)

## Action items for user (production)
1. Schema applied ✅ (production auth confirmed working)
2. Google OAuth enabled in Supabase ✅
3. Redirect URLs configured ✅ (https://valueweave.in/auth/callback)

## Backlog
### P0 (next session candidates)
- Email OTP fallback (Supabase native)
- Profile picture upload (Supabase Storage)
- Connection acceptance reveals contact (email or WhatsApp link)
- Realtime connection inbox badge

### P1
- Filter feed by location
- "Suggested opportunities" based on profile skills/interests
- Mentor flag
- SEO: server-render opportunity detail + profile (currently client-rendered)
- Vercel Analytics

### P2
- AI smart matching
- Local-language support (Hindi/Marathi)
- Trust badges / reputation from completed connections
- In-app messaging

## Tech debt
- `/profile/[userId]/page.js` imports `ProfileView` from `../page` (cross-segment). Move to `/components/ProfileView.jsx` next refactor.
- AppNavbar creates a new supabase client on each render — memoize.

## Test pass history
- iteration_1: 100% functional, 2 mobile overflow fixes applied
- iteration_2: 100% (12/12) polish-pass items verified — typography migration, public pages, '29 states', diversified suggestions, no hardcoded URLs, mobile UX
