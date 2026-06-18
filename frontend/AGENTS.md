# Frontend

## Purpose

Next.js frontend for CVBooster.

Provides UI for:
- User authentication
- Uploading CVs
- Scraping/pasting job descriptions
- Generating and previewing tailored CVs
- Selecting templates

## Ownership

- Frontend service owner
- Owns `frontend/`, including Next.js configuration, source code, assets, and dependencies
- Consumes the backend API
- Uses Supabase client libraries for authentication/session handling
- Deployed behind Nginx

## Local Contracts

- Next.js App Router
- TypeScript
- Tailwind CSS
- React Hook Form + Zod for form validation
- TanStack React Query for API data
- Zustand for client state
- Framer Motion for animations
- API calls use `/api` relative routes through Nginx
- Auth callback routing in `src/app/auth/callback/route.ts`
- Middleware protects authenticated routes

## Work Guidance

- Add pages under `src/app/`
- Add shared components under `src/components/`
- Keep API integration in `src/lib/api-client.ts`
- Keep Supabase client/server helpers in `src/lib/supabase/`
- Keep global CV state in `src/store/cv-store.ts`
- Prefer explicit types for API responses
- Do not embed backend secrets in client code

## Verification

- `cd frontend && npm run lint`
- `cd frontend && npm run build`

## Child DOX Index

- `src/AGENTS.md` — Frontend source: app routes, lib, hooks, store, middleware
