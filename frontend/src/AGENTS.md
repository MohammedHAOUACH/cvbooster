# Frontend Source

## Purpose

Frontend application source for CVBooster UI, routing, state, API client, and auth.

## Ownership

- Frontend developers and agents working under `frontend/`
- Each folder owns its UI/state integration boundary

## Local Contracts

- `app/`
  - `page.tsx` — landing page
  - `login/page.tsx` — login page (stores the `?token=` returned by the OAuth callback)
  - `dashboard/` — authenticated dashboard (list/download/delete CVs and jobs)
  - `create/page.tsx` — CV creation flow
  - `preview/[id]/page.tsx` — generated CV preview (authed PDF blob + retemplate)
- `lib/api-client.ts` — axios instance, auth interceptor, blob helpers, `endpoints`
- `lib/auth/client.ts` — localStorage JWT helpers
- `hooks/use-auth.ts` — authentication hooks
- `store/cv-store.ts` — Zustand store for CV flow state
- `globals.css` — global styles and Tailwind setup

## Work Guidance

- Keep API calls routed through the shared API client
- Keep route handlers minimal and data-driven
- Add new UI pages/components with corresponding types for expected API shapes
- PDFs are always fetched with `fetchAuthedBlob` (never via raw URL navigation)

## Verification

- `cd frontend && npm run lint`
- `cd frontend && npm run build`

## Child DOX Index

No child DOX files yet.
