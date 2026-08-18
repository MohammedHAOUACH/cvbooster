# Backend

## Purpose

FastAPI Python backend for CVBooster.

Provides authenticated APIs for:
- Uploading and parsing CV PDFs
- Scraping/pasting job descriptions
- Generating tailored ATS-friendly CV PDFs
- Listing/selecting CV templates

## Ownership

- Backend service owner
- Owns `backend/`, including Python dependencies, Dockerfile, and source code
- Depends on environment variables for external services
- Consumed by the Next.js frontend and the Nginx reverse proxy

## Local Contracts

- Python 3.12
- FastAPI application lives in `src/main.py`
- Route handlers in `src/routers/`
- Business logic in `src/services/`
- Pydantic models in `src/models/`
- Jinja2 CV HTML templates in `src/templates/`
- Configuration from `.env` via `src/config.py`
- Storage: SQLite via SQLAlchemy (`src/database.py`, `src/services/sqlite_storage.py`)
- Auth: signed JWT (HS256, `JWT_SECRET`) issued by the Google OAuth flow
  (`src/services/google_auth.py`); unsigned tokens are rejected; `SKIP_AUTH`
  disables auth for development only
- PDF parsing uses LiteParse
- Web scraping uses crawl4ai, guarded by `is_safe_url_for_scraping`
  (public http/https URLs only — no internal/private addresses)
- Language detection uses langdetect
- LLM generation uses LiteLLM (OpenRouter or local OpenAI-compatible server)
- PDF rendering uses WeasyPrint
- Job language detection runs on scrape/paste
- Generated CV output language defaults to detected job language
- Detected original CV style is stored on upload and used as default template
- Deleting an original CV or job cascades to the generated CVs built from it
- PDF files are only served to their owner (`/api/files/*` requires auth)
- Template catalog single source of truth: `src/services/cv_templates.py`

## Work Guidance

- Add new API endpoints in the matching router module
- Add service logic, not route-level business rules
- Keep Pydantic schemas explicit and validated
- Keep templates small and ATS-friendly
- Do not expose backend secrets through API responses
- Update `backend/requirements.txt` when adding runtime dependencies
- CPU-bound work (PDF parsing/rendering) must run via `asyncio.to_thread`
- Never fetch user-supplied URLs without the SSRF guard
- Sanitize client file names before writing to disk

## Verification

- `cd backend && python3 -m py_compile src/main.py`
- Test suite (from the repo root, uses the built backend image):
  `docker run --rm -v $(pwd)/backend:/app -w /app cvbooster-api sh -c "pip install -q pytest && python -m pytest tests -q"`
- Optional: start backend with `uvicorn src.main:app --reload --port 8000` and verify `/docs`

## Child DOX Index

- `src/AGENTS.md` — Backend source modules, routers, services, models, templates, utils
