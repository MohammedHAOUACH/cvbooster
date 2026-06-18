# Backend

## Purpose

FastAPI Python backend for CVBooster.

Provides authenticated APIs for:
- Uploading and parsing CV PDFs
- Scraping job descriptions
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
- Database/storage/auth integration via `src/database.py` and `src/services/supabase_service.py`
- PDF parsing uses LiteParse
- Web scraping uses crawl4ai
- LLM generation uses LiteLLM with OpenRouter
- PDF rendering uses WeasyPrint

## Work Guidance

- Add new API endpoints in the matching router module
- Add service logic, not route-level business rules
- Keep Pydantic schemas explicit and validated
- Keep templates small and ATS-friendly
- Do not expose backend secrets through API responses
- Update `backend/requirements.txt` when adding runtime dependencies

## Verification

- `cd backend && python -m py_compile src/main.py`
- Optional: start backend with `uvicorn src.main:app --reload --port 8000` and verify `/docs`

## Child DOX Index

- `src/AGENTS.md` — Backend source modules, routers, services, models, templates, utils
