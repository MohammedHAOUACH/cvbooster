# Nginx

## Purpose

Reverse proxy for local CVBooster deployment.

Routes:
- `/api` to the FastAPI backend
- remaining routes to the Next.js frontend

## Ownership

- Deployment configuration owner
- Owns `nginx/nginx.conf`
- Depends on backend and frontend running on expected internal ports

## Local Contracts

- Nginx Alpine image
- Single config file: `nginx/nginx.conf`
- Listens on port 80
- Routes are mounted by Docker Compose via volume bind
- Upstreams use Docker Compose **service names** (`api`, `frontend`) — not
  hardcoded container names
- API routes use relative `/api` prefix; long LLM timeouts on `/api/`
- Frontend is served as static/Node application behind proxy

## Work Guidance

- Keep config minimal
- Mirror route changes in backend/frontend here when public path changes
- Do not add backend secrets or credentials here

## Verification

- `docker compose up --build`
- Verify:
  - `http://localhost/api/docs`
  - `http://localhost`

## Child DOX Index

No child DOX files yet.
