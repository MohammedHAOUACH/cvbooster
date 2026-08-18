# Backend Source

## Purpose

Implementation packages for CVBooster backend logic, APIs, models, templates, and configuration.

## Ownership

- Backend developers and agents working under `backend/`
- Each subpackage owns its responsibility boundary

## Local Contracts

- `config.py` — application settings and environment variables (single source: `get_settings()`)
- `database.py` — SQLAlchemy engine/session/models (SQLite; tz-aware UTC timestamps)
- `routers/` — FastAPI route handlers
  - `auth.py` — session, profile, Google OAuth initiation/callback
  - `cv_engine.py` — generate, list, get, download, delete, retemplate
  - `files.py` — authenticated PDF serving (original + generated)
  - `scraper.py` — job scrape (SSRF-guarded) / paste / list / delete
  - `templates.py` — template catalog (from `services/cv_templates.py`)
  - `upload.py` — CV upload (PDF magic-byte check, size cap, sanitized names)
- `services/` — business logic
  - `ats_optimizer.py`
  - `cv_templates.py`
  - `google_auth.py`
  - `job_scraper.py`
  - `llm_service.py`
  - `pdf_generator.py`
  - `pdf_parser.py`
  - `sqlite_storage.py`
- `models/` — Pydantic request/response schemas
  - `cv.py`
  - `job.py`
  - `response.py`
  - `user.py`
- `templates/` — Jinja2 HTML templates for PDF CV generation
  - `base.html`
  - `clean.html`
  - `modern.html`
  - `minimal.html`
  - `corporate.html`
  - `tech.html`
  - `creative.html`
  - `academic.html`
  - `executive.html`
- `utils/` — backend utilities
  - `auth.py` — JWT verification dependency
  - `validators.py` — URL validation + SSRF guard

## Work Guidance

- Routers call services, not each other
- Services own external calls: database, storage, LLM, parsing, scraping
- Models validate input/output shapes before services use them
- Templates receive validated model fields and avoid complex layout
- Job language is detected on scrape/paste and stored on job posting
- Generated CV output language defaults to detected job language
- Original CV style/format is detected during PDF parsing and stored on upload
- Default generated template preserves original CV style when possible
- Delete operations cascade to dependent generated CVs (DB rows + PDF files)

## Verification

- `cd backend && python3 -m py_compile src/main.py`
- `pytest` suite in `backend/tests/` (see backend/AGENTS.md)

## Child DOX Index

No child DOX files yet.
