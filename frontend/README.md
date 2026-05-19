# ValueWeave

India's collaboration and opportunity discovery platform — where ambition finds its team.

## Stack
- **Next.js 14** (App Router) — frontend & server actions
- **Supabase** — Postgres + Auth (Google OAuth) + Row-Level Security
- **Tailwind CSS** — design
- **Vercel** — deployment

No separate backend. Everything talks to Supabase directly.

## Setup (one-time)
1. **Apply the database schema**
   - Open Supabase Dashboard → SQL Editor.
   - Paste the contents of `supabase_schema.sql` and run.

2. **Enable Google OAuth**
   - Supabase Dashboard → Authentication → Providers → Google → enable.
   - You'll need a Google OAuth Client ID + Secret. Follow Supabase's guide: https://supabase.com/docs/guides/auth/social-login/auth-google

3. **Add redirect URLs**
   - Supabase Dashboard → Authentication → URL Configuration → Redirect URLs, add:
     - `https://<your-vercel-domain>/auth/callback`
     - `http://localhost:3000/auth/callback`
     - Your preview URL `/auth/callback`

4. **Environment variables** — `/app/frontend/.env.local`
   ```
   NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOi...
   ```

## Local dev
```
cd /app/frontend
yarn install
yarn dev
```
Open http://localhost:3000

## Deploy to Vercel
1. Push `/app/frontend` to GitHub.
2. Import repo into Vercel → Root directory: `frontend`.
3. Add the two env vars above in Vercel.
4. Update Supabase Redirect URLs with the Vercel domain.

## Routes
- `/` — Landing
- `/get-started` — Intent selection → Google sign-in
- `/auth/callback` — OAuth code exchange
- `/onboarding` — Profile setup
- `/dashboard` — Opportunity feed
- `/opportunities/new` — Post an opportunity
- `/opportunities/[id]` — Opportunity detail + connect
- `/profile` — My profile
- `/profile/[userId]` — Other user
- `/connections` — Sent & received requests

## Architecture
```
Frontend (Next.js) ──► Supabase (Auth, Postgres, RLS)
                              │
                              └──► browser holds session cookie
                                   (refreshed by middleware.js)
```
