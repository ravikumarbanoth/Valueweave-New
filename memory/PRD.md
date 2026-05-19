# ValueWeave — PRD (Living Document)

## Vision
ValueWeave is a collaboration and opportunity discovery platform for India's tier-2/tier-3 builders. Connect students, freelancers, skilled workers, and entrepreneurs to discover collaborators, form startup teams, and create real economic opportunities. Not a job portal, not LinkedIn, not Fiverr — a productive collaboration ecosystem.

## Architecture (final, simple)
- **Frontend:** Next.js 14 (App Router) in `/app/frontend`
- **Backend / DB / Auth:** Supabase (Postgres + RLS + Google OAuth)
- **No separate backend service**
- **Styling:** Tailwind CSS, mobile-first
- **Deployment:** Vercel (frontend) — Supabase manages the rest

## Users
Students · Unemployed youth · AI learners · Local entrepreneurs · Skilled workers · Freelancers · Startup builders · Tier-2/3 opportunity seekers

## What's been implemented (MVP v1 — 2026-01)
1. **Landing page** — Hero, How It Works (4 steps), Opportunity Categories (8), Final CTA. Warm amber/teal palette, Syne + DM Sans, lightweight CSS animations.
2. **Get Started** — 8 intent cards, intent stored in localStorage + Supabase profile after OAuth.
3. **Authentication** — Supabase Google OAuth (Email OTP deferred to v2). `/auth/callback` exchanges code → routes to `/onboarding` or `/dashboard`.
4. **Protected route middleware** — `/dashboard`, `/onboarding`, `/opportunities`, `/profile`, `/connections` redirect unauthenticated users to `/`.
5. **Onboarding** — Lightweight profile: name, city, skills (chip input), interests, looking_for, short bio.
6. **Dashboard / Feed** — Opportunity list with category filter (8 categories), keyword search.
7. **Post Opportunity** — Title, description, category, skills_needed, location, collaboration_type, commitment.
8. **Opportunity Detail** — Full view + Connect modal (one request per opportunity per user). Owner can delete.
9. **Profile** — Mine (editable) + others (`/profile/[userId]`). Shows skills, interests, looking_for, posted opportunities.
10. **Connections** — Received/Sent tabs, accept/decline. Status: pending/accepted/rejected.
11. **Database schema** — `/app/frontend/supabase_schema.sql` with RLS policies (public read profiles/opportunities, owner-only writes, recipient-only status updates).
12. **Reusable components** — `AppNavbar` (desktop top + mobile bottom nav), `OpportunityCard`, chip inputs.

## Action items for user (required for the app to actually work end-to-end)
1. **Run schema SQL** — Supabase Dashboard → SQL Editor → paste `/app/frontend/supabase_schema.sql` → Run.
2. **Enable Google OAuth** — Supabase → Authentication → Providers → Google → enable. Add Google OAuth client ID + secret (follow Supabase's official guide).
3. **Add allowed redirect URLs** — Supabase → Authentication → URL Configuration → add:
   - `https://6ae7e30c-6a13-4f33-9a2b-6cf1a1124a32.preview.emergentagent.com/auth/callback`
   - Your Vercel domain `/auth/callback`
   - `http://localhost:3000/auth/callback` (for local dev)

## Prioritized Backlog
### P0 (do next session)
- Email OTP sign-in (alternative to Google) — Supabase native, low effort.
- Public read for opportunity detail and other-user profile (unauth viewers see the page; only "Connect" needs auth). Today middleware blocks them.
- "My opportunities" inline editing.
- Better empty states and skeleton loaders.

### P1
- Image upload on profile (Supabase Storage).
- Basic notifications (badge for unread connection requests).
- Filter feed by location.
- Connection acceptance opens a contact reveal (email or chat link).
- Vercel Analytics or Plausible for onboarding dropoff.

### P2
- AI smart matching ("opportunities for you" based on skills/interests)
- Mentor flag on profiles
- Local-language support (Hindi/Marathi first)
- Trust badges / reputation score from completed connections
- In-app messaging

## Known limitations / not implemented
- No Email OTP (deferred per user instruction).
- Resend / email automation deferred.
- No analytics yet.
- Connection updates require a manual page refresh (no realtime; could add Supabase Realtime later).

## Tech debt
- `profile/[userId]/page.js` imports `ProfileView` from `../page` which is a Next.js anti-pattern (importing client components across route segments). Acceptable for now; should be moved to `/components/ProfileView.jsx` in next refactor.
