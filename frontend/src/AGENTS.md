# Frontend Source

## Purpose

Frontend application source for CVBooster UI, routing, state, API client, and auth middleware.

## Ownership

- Frontend developers and agents working under `frontend/`
- Each folder owns its UI/state integration boundary

## Local Contracts

- `app/`
  - `page.tsx` — landing page
  - `login/page.tsx` — login page
  - `auth/callback/route.ts` — OAuth callback handling
  - `dashboard/` — authenticated dashboard
  - `create/page.tsx` — CV creation flow
  - `preview/[id]/page.tsx` — generated CV preview
- `lib/api-client.ts` — API request configuration and helpers
- `lib/supabase/`
  - `client.ts`
  - `server.ts`
- `hooks/use-auth.ts` — authentication hooks
- `store/cv-store.ts` — Zustand store for CV flow state
- `middleware.ts` — Next.js middleware for auth routing
- `globals.css` — global styles and Tailwind setup

## Work Guidance

- Keep API calls routed through the shared API client
- Keep Supabase usage in dedicated helpers
- Keep route handlers minimal and data-driven
- Add new UI pages/components with corresponding types for expected API shapes

## Verification

- `cd frontend && npm run lint`
- `cd frontend && npm run build`

## Child DOX Index

No child DOX files yet.
