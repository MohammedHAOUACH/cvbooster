# CVBooster

ATS-optimized CV generator. Upload your resume, add a job posting, and get a tailored ATS-friendly CV in seconds.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 15 + React 19 + Tailwind CSS |
| Backend | FastAPI (Python 3.12) |
| Database | SQLite (SQLAlchemy) |
| Auth | Google OAuth + signed JWT (HS256); `SKIP_AUTH` for development |
| PDF Parsing | LiteParse |
| Web Scraping | crawl4ai (SSRF-guarded) |
| LLM | LiteLLM: OpenRouter or local OpenAI-compatible server (llama.cpp/vLLM) |
| PDF Generation | WeasyPrint + Jinja2 |
| Deployment | Docker Compose + Nginx |

## Features

- **Auto language detection:** generated CV output language matches the detected job posting language (no manual selector)
- **Format preservation:** the original CV style is detected on upload and used as the default template
- **ATS optimization:** keyword matching with an honest coverage score
- **8 templates:** switch templates at any time (retemplate) without re-running the LLM
- **Owner-only files:** PDFs are served only to the user who uploaded/generated them
- **Cascade deletes:** deleting an original CV or a job posting also removes the CVs generated from it

## Quick Start (Docker)

### 1. Setup Environment

```bash
cp .env.example .env
# Edit .env: Google OAuth credentials, JWT_SECRET, and LLM access
# (OpenRouter key or local LLM URL)
```

### 2. Run

```bash
docker compose up --build
```

Services are available at:

- Frontend: http://localhost
- API docs: http://localhost/api/docs
- Health check: http://localhost/api/health

### 3. Development Without Authentication

`SKIP_AUTH` in `.env` disables auth (development only). It must be in sync
on both sides — docker-compose already wires `SKIP_AUTH` into the frontend
build as `NEXT_PUBLIC_SKIP_AUTH`:

```bash
# In .env
SKIP_AUTH=true
docker compose up --build
```

## Local Development (without Docker)

### Backend

```bash
cd backend
pip install -r requirements.txt
# Set SKIP_AUTH=true (and .env in the repo root) for auth-less dev
uvicorn src.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
# frontend/.env.local: NEXT_PUBLIC_API_URL=/api and
# NEXT_PUBLIC_SKIP_AUTH=true (must match the backend SKIP_AUTH)
npm run dev
```

In dev, `/api/*` is proxied to `http://localhost:8000` by Next.js rewrites
(`next.config.ts`). In production, Nginx serves `/api/` directly.

## VPS Deployment

For the complete VPS guide (Google OAuth, SQLite, Nginx, small-VPS sizing):

👉 **See [DEPLOYMENT.md](DEPLOYMENT.md)**

Setup helpers:

- `scripts/init.sh` — creates upload/data dirs and generates `JWT_SECRET`
- `scripts/test-deployment.sh` — smoke-tests a running deployment

## Project Structure

```
cvbooster/
├── backend/
│   ├── src/
│   │   ├── main.py        # FastAPI app factory
│   │   ├── config.py      # Settings (single source: get_settings())
│   │   ├── database.py    # SQLAlchemy models (SQLite)
│   │   ├── routers/       # API endpoints (auth, upload, jobs, cv, templates, files)
│   │   ├── services/      # Business logic (LLM, parsing, scraping, storage, templates)
│   │   ├── models/        # Pydantic request/response schemas
│   │   ├── templates/     # Jinja2 CV HTML templates
│   │   └── utils/         # JWT auth dependency, URL/SSRF validators
│   ├── tests/             # Pytest suite
│   ├── data/              # SQLite database (created at runtime)
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/           # Pages & layouts (landing, login, dashboard, create, preview)
│   │   ├── components/    # React components
│   │   ├── hooks/         # use-auth
│   │   ├── lib/           # API client (axios + authed blob fetch)
│   │   └── store/         # Zustand CV flow state
│   └── Dockerfile
├── uploads/               # CV PDFs (original-cvs/ + generated-cvs/)
├── nginx/                 # Reverse proxy config (/api -> backend, rest -> frontend)
├── scripts/               # Deployment helpers
├── docker-compose.yml
└── .env                   # Environment variables (from .env.example)
```

## API Endpoints

All endpoints require `Authorization: Bearer <jwt>` unless `SKIP_AUTH=true`.

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/session` | Get current user profile |
| PUT | `/api/auth/profile` | Update name/avatar |
| POST | `/api/auth/logout` | Logout (client-side token removal) |
| GET | `/api/auth/google` | Start Google OAuth flow |
| GET | `/api/auth/google/callback` | Google OAuth callback (redirects to `/login?token=...`) |

### CV Upload

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload/cv` | Upload CV PDF (parsed + style detected) |
| GET | `/api/upload/cvs` | List original CVs |
| GET | `/api/upload/cv/{id}` | Get one original CV |
| DELETE | `/api/upload/cv/{id}` | Delete original CV + cascade to generated CVs |

### Job Postings

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/jobs/scrape` | Scrape job URL (SSRF-guarded, public http/https only) |
| POST | `/api/jobs/paste` | Paste job text (language detected) |
| GET | `/api/jobs` | List job postings |
| GET | `/api/jobs/{id}` | Get one job posting |
| DELETE | `/api/jobs/{id}` | Delete job + cascade to generated CVs |

### CV Generation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/cv/generate` | Generate tailored CV (LLM + PDF) |
| GET | `/api/cv` | List generated CVs |
| GET | `/api/cv/{id}` | Get one generated CV |
| GET | `/api/cv/{id}/download` | Download PDF |
| POST | `/api/cv/{id}/retemplate` | Re-render with another template |
| DELETE | `/api/cv/{id}` | Delete generated CV |

### Templates & Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/templates` | List templates (catalog source: `services/cv_templates.py`) |
| GET | `/api/templates/{name}` | Get one template |
| GET | `/api/files/original-cvs/{path}` | Owner-only original PDF serving |
| GET | `/api/files/generated-cvs/{path}` | Owner-only generated PDF serving |

### Misc

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |

## CV Templates

8 ATS-friendly templates: Clean, Modern, Minimal, Corporate, Tech, Creative,
Academic, Executive. Detected styles map to templates so the default generated
CV keeps the original format.

## Configuration

`.env.example` is the single source of truth for environment variables. Key
settings:

```env
# Auth
SKIP_AUTH=false                      # true = dev mode, no login
GOOGLE_CLIENT_ID=...                 # Google OAuth (see OAUTH-SETUP.md)
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://<host>/api/auth/google/callback
JWT_SECRET=...                       # sign/verify local JWTs

# LLM (one of)
OPENROUTER_API_KEY=...
USE_OPENROUTER=true
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct
# or local OpenAI-compatible server:
LOCAL_LLM_URL=http://localhost:1234
LOCAL_LLM_MODEL=...

# Storage
DATABASE_PATH=...                    # default: backend/data/cvbooster.db
UPLOADS_DIR=/app/uploads
```

Frontend build-time vars (`NEXT_PUBLIC_*` are baked in at build time):
`NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SKIP_AUTH` — wired in `docker-compose.yml`.

## Testing

Backend suite (from the repo root, uses the built backend image):

```bash
docker run --rm -v $(pwd)/backend:/app -w /app cvbooster-api \
  sh -c "pip install -q pytest && python -m pytest tests -q"
```

Frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

### Manual API Flow

Use the Swagger UI at `http://localhost:8000/docs` (or `/api/docs` behind
Nginx), or with curl when `SKIP_AUTH=true` (any Bearer token is accepted):

```bash
# Upload CV
curl -X POST http://localhost:8000/api/upload/cv \
  -H "Authorization: Bearer dummy" \
  -F "file=@/path/to/cv.pdf"

# Paste job
curl -X POST http://localhost:8000/api/jobs/paste \
  -H "Authorization: Bearer dummy" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Software Engineer",
    "company": "Tech Company",
    "raw_content": "We are looking for a Python developer..."
  }'

# Generate CV (use the IDs from the previous responses)
curl -X POST http://localhost:8000/api/cv/generate \
  -H "Authorization: Bearer dummy" \
  -H "Content-Type: application/json" \
  -d '{
    "original_cv_id": "xxx",
    "job_posting_id": "yyy",
    "template_name": "clean"
  }'
```

## Troubleshooting

```bash
# Rebuild from scratch
docker compose down -v
docker compose build --no-cache
docker compose up -d

# Reset database (drops SQLite + uploaded files)
docker compose down -v
docker compose up -d

# Logs
docker compose logs -f api
docker compose logs -f frontend
```

Notes:

- Scraping is blocked for internal/private URLs (SSRF guard) and often
  fails on anti-bot sites — use "Paste Text" mode for those.
- `SKIP_AUTH` must be `true` on **both** backend and frontend to work.
- Frontend `NEXT_PUBLIC_*` vars change only after a rebuild
  (`docker compose build frontend`).
