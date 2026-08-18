# Frontend

## Purpose

Next.js frontend for CVBooster.

Provides UI for:
- User authentication (Google OAuth via the backend)
- Uploading CVs
- Scraping/pasting job descriptions
- Generating and previewing tailored CVs
- Selecting templates
- Managing (list/download/delete) original and generated CVs

## Ownership

- Frontend service owner
- Owns `frontend/`, including Next.js configuration, source code, assets, and dependencies
- Consumes the backend API
- Deployed behind Nginx

## Local Contracts

- Next.js App Router
- TypeScript
- Tailwind CSS
- React Hook Form + Zod available for form validation
- TanStack React Query available for API data
- Zustand for client state (`src/store/cv-store.ts`)
- API calls use relative `/api` routes:
  - production: proxied by Nginx to the FastAPI backend
  - dev (`npm run dev`): proxied by Next.js rewrites in `next.config.ts`
- Auth: the JWT returned by the backend Google flow is stored in localStorage
  (`src/lib/auth/client.ts`) and attached by the axios interceptor in
  `src/lib/api-client.ts`; protected files (PDFs) are fetched as blobs with the
  auth header (`fetchAuthedBlob` / `downloadBlob`)
- `NEXT_PUBLIC_SKIP_AUTH=true` builds a dev front-end without sign-in; it must
  stay in sync with the backend `SKIP_AUTH` (wired in docker-compose.yml)

## Work Guidance

- Add pages under `src/app/`
- Add shared components under `src/components/`
- Keep API integration in `src/lib/api-client.ts` (all endpoints live in `endpoints`)
- Prefer explicit types for API responses (`src/store/cv-store.ts`)
- Do not embed backend secrets in client code
- Do not display fabricated metrics (scores, counts) — show "—" when absent

## Verification

- `cd frontend && npm run lint`
- `cd frontend && npm run build`

## Child DOX Index

- `src/AGENTS.md` — Frontend source: app routes, lib, hooks, store
