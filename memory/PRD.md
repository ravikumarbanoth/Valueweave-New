# ValueWeave — PRD (Living Document)

## Vision
ValueWeave is a collaboration and opportunity discovery platform for India's tier-2/tier-3 builders. Connect students, freelancers, skilled workers, and entrepreneurs to discover collaborators, form startup teams, and create real economic opportunities. Not a job portal, not LinkedIn, not Fiverr — a productive collaboration ecosystem.

## Architecture
- **Frontend:** Next.js 14 (App Router) in `/app/frontend`
- **Backend / DB / Auth:** Supabase (Postgres + RLS + Google OAuth)
- **No separate backend service**
- **Typography:** Plus Jakarta Sans (display) + Inter (body) via `next/font`
- **Styling:** Tailwind CSS, mobile-first
- **Deployment:** Vercel — production at https://valueweave.in

## Public routes (no auth)
`/` · `/get-started` · `/signin` · `/explore` · `/about` · `/privacy` · `/terms` · `/opportunities/[id]` · `/profile/[userId]` · `/auth/callback`

## Protected routes (Supabase session required)
`/dashboard` · `/onboarding` · `/opportunities/new` · `/profile` (self) · `/connections`

## Smart auth flow
- **Landing CTAs**: "Join ValueWeave" (new) → `/get-started`; "Sign in" (returning) → `/signin`
- **`/signin`**: If session exists → smart redirect (`profile_complete ? /dashboard : /onboarding`). If not → Google OAuth.
- **`/auth/callback`**: Exchanges code, persists `looking_for` from intent query if present, then routes to `/dashboard` or `/onboarding` based on `profile_complete`.
- **Middleware**: refreshes session on every request, gates protected routes.

## Implemented features
1. Landing — dual CTAs, trust signals (Google-auth · Mobile-first · Free to join), "Why ValueWeave Exists" gap-narrative, How-it-works, Categories, Final CTA, expanded 4-column footer with About/Privacy/Terms/Contact.
2. Get Started — 8 intent cards, "Already a member? Sign in →" link.
3. Sign in — Welcome-back page with Google OAuth + smart redirect.
4. Onboarding — lightweight profile (name, city, skills, interests, looking_for, bio), 35 Bharat-inclusive skill suggestions + 23 interests.
5. Dashboard / Feed — filters, search, skeleton loaders, profile-completion banner.
6. Post Opportunity — full form.
7. Opportunity Detail — public-readable, WhatsApp + Copy-link Share, anon "Sign in to connect" CTA, owner delete.
8. Profile (mine + others) — public-readable for others.
9. Connections — Sent/Received tabs with tab-specific empty states + CTAs.
10. Explore — public feed without auth.
11. About / Privacy / Terms — info pages via shared `LegalShell` component.
12. Footer with `valueweave.team@gmail.com` contact.

## Production readiness
- No hardcoded `localhost` / `vercel.app` / `127.0.0.1` URLs (grep verified)
- All OAuth redirects use `window.location.origin` (browser) or request URL `origin` (server)
- `metadataBase: https://valueweave.in` + OG tags
- Mobile-first: 44px min touch targets, safe-area inset bottom nav
- Reduced shadow intensity for premium feel
- All public pages 200, protected pages 307 → `/?auth=required`

## Test pass history
- iteration_1 (initial build): 100% functional, 2 minor mobile responsive fixes applied
- iteration_2 (typography + public share + diversified suggestions): 12/12 100% pass
- iteration_3 (smart auth + trust polish + legal pages): 13/13 100% pass
- iteration_4 (Bharat-rebalance + trust-first connection UX): 13/13 100% pass

## Iteration 4 changes (2026-01)
- **Bharat-balanced landing labels:** AI · Hyderabad, Agri · Warangal, Retail · Vijayawada, EV · Coimbatore
- **Why-section copy:** mentions Warangal, Vizag, Guntur, Hyderabad, Vijayawada, Coimbatore
- **Onboarding + Post-Opportunity placeholders:** "Hyderabad, Telangana"
- **Trust-first connections:** No auto-reveal of phone/email/WhatsApp. Accepted state shows soft-green styling + explicit helper: "Connection accepted. You can now safely share contact details if you'd like to collaborate further. ValueWeave keeps contact sharing manual to protect your privacy."
- **OpportunityCard:** prominent 3-tag header row (category · collaboration_type · commitment) + MapPin location pill
- **Dashboard feed nearby boost:** Items whose location substring-matches user's city are floated to the top with a "Nearby" badge (`data-testid=opp-nearby-*`). Otherwise newest-first.

## Backlog
### P0
- Email OTP fallback (Supabase native, low effort)
- Connection acceptance reveals contact (WhatsApp/email)
- Profile picture upload (Supabase Storage)
- Realtime inbox badge for unread connection requests
- Server-render `/opportunities/[id]` + `/profile/[userId]` for SEO

### P1
- Feed location filter
- "Suggested for you" based on profile skills/interests
- Mentor flag
- Vercel Analytics / Plausible

### P2
- AI smart matching
- Hindi / Marathi i18n
- Trust badges / reputation from completed connections
- In-app messaging

## Tech debt resolved
- `LegalShell` now lives in `/components/LegalShell.jsx` (was in `app/about/page.js`)
