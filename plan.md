# Plan: Auto language, preserve original CV format, store detection

**DOX Chain:**
- `AGENTS.md`
- `backend/AGENTS.md`
- `backend/src/AGENTS.md`

**DOX Constraints:**
- Routers call services, not each other.
- Services own external calls and parsing logic.
- Models validate input/output shapes.
- Update nearest AGENTS.md after meaningful changes.
- Keep docs concise, remove stale text.

## Context

- Generated CV must use the same language as the job posting.
- Default style should preserve the original CV format when possible.
- No manual language selector required.
- Store detected job language and output language in DB.

## Tasks

### 1. Database schema
- Add:
  - `job_postings.detected_language TEXT`
  - `generated_cvs.output_language TEXT`
  - `generated_cvs.original_cv_style TEXT`
- Update `docker-db/setup.sql`.

### 2. Backend models
- Add fields to:
  - `backend/src/models/job.py`
  - `backend/src/models/cv.py`
- Ensure optional fields with defaults.

### 3. Job language detection
- Detect language from `raw_content` before LLM.
- Default to `en` if undetectable.
- Store on job posting.

### 4. Original CV format detection
- Parse original PDF to infer style/format:
  - section structure/order
  - presence of sidebar/layout columns
  - color usage vs grayscale
  - dominant font style
- Map detected style to closest existing template.
- Fallback to `clean`.

### 5. LLM prompt update
- Add target language instruction.
- Add preserve original structure/format intent instruction.
- Keep JSON Resume output contract.

### 6. PDF generator localization
- Use dynamic section headers based on target language.
- Support French/English defaults, extendable.
- Update HTML lang attribute.

### 7. CV generation router
- Use detected original style as default template.
- Use detected job language as output language.
- Store detection fields on generated CV record.

### 8. Frontend store/types
- Add optional detected language/style fields to generated CV type.
- Keep API client compatible.

### 9. Verification
- `cd backend && python3 -m py_compile src/main.py`
- Optional frontend lint/build.

### 10. DOX closeout
- Update affected AGENTS.md files.
- Refresh Child DOX Index entries.
- Remove stale text.

## Files to touch

- `docker-db/setup.sql`
- `backend/src/models/cv.py`
- `backend/src/models/job.py`
- `backend/src/services/pdf_parser.py`
- `backend/src/services/llm_service.py`
- `backend/src/services/pdf_generator.py`
- `backend/src/routers/cv_engine.py`
- `backend/src/routers/scraper.py`
- `backend/requirements.txt`
- `frontend/src/store/cv-store.ts`
- `AGENTS.md`
- `backend/AGENTS.md`
- `backend/src/AGENTS.md`
- `docker-db/AGENTS.md`
