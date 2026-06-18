# Backend Source

## Purpose

Implementation packages for CVBooster backend logic, APIs, models, templates, and configuration.

## Ownership

- Backend developers and agents working under `backend/`
- Each subpackage owns its responsibility boundary

## Local Contracts

- `config.py` — application settings and environment variables
- `database.py` — database/session/connection setup
- `routers/` — FastAPI route handlers
  - `auth.py`
  - `cv_engine.py`
  - `files.py`
  - `scraper.py`
  - `templates.py`
  - `upload.py`
- `services/` — business logic
  - `ats_optimizer.py`
  - `job_scraper.py`
  - `llm_service.py`
  - `pdf_generator.py`
  - `pdf_parser.py`
  - `supabase_service.py`
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
  - `auth.py`
  - `validators.py`

## Work Guidance

- Routers call services, not each other
- Services own external calls: database, storage, LLM, parsing, scraping
- Models validate input/output shapes before services use them
- Templates receive validated model fields and avoid complex layout
- Job language is detected on scrape/paste and stored on job posting
- Generated CV output language defaults to detected job language
- Original CV style/format is detected during PDF parsing
- Default generated template preserves original CV style when possible

## Verification

- `cd backend && python -m py_compile src/main.py`
- Optional lint/type checks if configured

## Child DOX Index

No child DOX files yet.
