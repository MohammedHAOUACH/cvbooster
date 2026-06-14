# CVBooster

ATS-optimized CV generator. Upload your resume, add a job posting, and get a tailored ATS-friendly CV in seconds.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 15 + React 19 + Tailwind CSS |
| Backend | FastAPI (Python 3.12) |
| Database | Supabase (PostgreSQL + Auth + Storage) |
| Auth | Google, Facebook, TikTok (OAuth) |
| PDF Parsing | LiteParse |
| Web Scraping | crawl4ai |
| LLM | OpenRouter (via litellm) |
| PDF Generation | WeasyPrint + Jinja2 |
| Deployment | Docker Compose |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Supabase account (free tier)
- OpenRouter API key (for LLM)

### 1. Setup Supabase

1. Create a project at https://supabase.com/dashboard
2. Enable OAuth providers (Google, Facebook) in **Authentication > Providers**
3. For TikTok: use **Custom OAuth Provider**
4. Run the SQL setup script:
   - Go to **SQL Editor** in Supabase dashboard
   - Copy and paste the contents of `docker-db/setup.sql`
   - Run the script

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your Supabase credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key
OPENROUTER_API_KEY=sk-or-...
```

### 3. Run with Docker

```bash
# Development
docker compose up --build

# Production
docker compose up -d
```

Services will be available at:
- Frontend: http://localhost
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 4. Development Mode

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Project Structure

```
cvbooster/
├── backend/            # FastAPI Python backend
│   ├── src/
│   │   ├── routers/    # API endpoints
│   │   ├── services/   # Business logic
│   │   ├── models/     # Pydantic schemas
│   │   ├── templates/  # Jinja2 CV templates
│   │   └── utils/      # Auth, validation
│   └── Dockerfile
├── frontend/           # Next.js React frontend
│   ├── src/
│   │   ├── app/        # Pages & layouts
│   │   ├── components/ # React components
│   │   ├── lib/        # Supabase, API client
│   │   └── hooks/      # Custom hooks
│   └── Dockerfile
├── docker-compose.yml
├── nginx/              # Reverse proxy config
└── docker-db/          # SQL setup scripts
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/session` | Get current user |
| POST | `/api/upload/cv` | Upload CV PDF |
| POST | `/api/jobs/scrape` | Scrape job URL |
| POST | `/api/jobs/paste` | Paste job text |
| POST | `/api/cv/generate` | Generate CV |
| GET | `/api/cv/{id}/download` | Download PDF |
| GET | `/api/templates` | List templates |

## CV Templates

8 ATS-friendly templates: Clean, Modern, Minimal, Corporate, Tech, Creative, Academic, Executive

## License

MIT
