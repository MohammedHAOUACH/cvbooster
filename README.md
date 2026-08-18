# CVBooster

ATS-optimized CV generator. Upload your resume, add a job posting, and get a tailored ATS-friendly CV in seconds.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 15 + React 19 + Tailwind CSS |
| Backend | FastAPI (Python 3.12) |
| Database | SQLite (SQLAlchemy) |
| Auth | Google OAuth + signed JWT (or `SKIP_AUTH` for dev) |
| PDF Parsing | LiteParse |
| Web Scraping | crawl4ai |
| LLM | LiteLLM: OpenRouter or local OpenAI-compatible server (llama.cpp/vLLM) |
| PDF Generation | WeasyPrint + Jinja2 |
| Deployment | Docker Compose |

## Quick Start (Local Development)

### Prerequisites

- Docker & Docker Compose
- OpenRouter API key (for LLM) - optional, can use local LLM

### 1. Setup Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 2. Run with Docker

```bash
# Development (with SKIP_AUTH=true)
docker compose up --build

# Production mode
docker compose up -d
```

Services will be available at:
- Frontend: http://localhost
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 3. Development Mode (without Docker)

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

## VPS Deployment

For complete VPS deployment guide with Google OAuth, SQLite, and free OpenRouter model:

👉 **See [DEPLOYMENT.md](DEPLOYMENT.md)**

Key features:
- SQLite database (no external DB needed)
- Google OAuth authentication
- Free OpenRouter model (tencent/hy3:free)
- Full Docker Compose setup
- Cost: ~5€/month on small VPS

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
│   ├── data/           # SQLite database (created at runtime)
│   └── Dockerfile
├── frontend/           # Next.js React frontend
│   ├── src/
│   │   ├── app/        # Pages & layouts
│   │   ├── components/ # React components
│   │   ├── lib/        # API client
│   │   └── store/      # State management
│   └── Dockerfile
├── uploads/            # CV files (original & generated)
├── nginx/              # Reverse proxy config
├── scripts/            # Deployment scripts
├── docker-compose.yml
└── .env                # Environment variables
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/session` | Get current user |
| GET | `/api/auth/google` | Google OAuth login |
| GET | `/api/auth/google/callback` | Google OAuth callback |
| POST | `/api/upload/cv` | Upload CV PDF |
| GET | `/api/upload/cvs` | List uploaded CVs |
| POST | `/api/jobs/scrape` | Scrape job URL |
| POST | `/api/jobs/paste` | Paste job text |
| GET | `/api/jobs` | List job postings |
| POST | `/api/cv/generate` | Generate CV |
| GET | `/api/cv/{id}/download` | Download PDF |
| GET | `/api/templates` | List templates |

## CV Templates

8 ATS-friendly templates: Clean, Modern, Minimal, Corporate, Tech, Creative, Academic, Executive

## Configuration

### Environment Variables

See `.env.example` for all available options:

```env
# App
APP_NAME=CVBooster
APP_ENV=development
CORS_ORIGINS=http://localhost:3000,http://localhost:80
DEBUG=false
SKIP_AUTH=true  # Set to false in production

# Database
DATABASE_PATH=/app/data/cvbooster.db

# Google OAuth (for VPS deployment)
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REDIRECT_URI=http://your-vps-ip/api/auth/google/callback
JWT_SECRET=xxx

# OpenRouter (free model)
OPENROUTER_API_KEY=sk-or-xxx
USE_OPENROUTER=true

# Local LLM (fallback)
LOCAL_LLM_URL=http://localhost:1234
LOCAL_LLM_MODEL=Qwen3.6-27B-UD-Q5_K_XL.gguf
```

### Features

- **Auto language detection:** CV output language matches job posting language
- **Format preservation:** Original CV style is preserved when possible
- **ATS optimization:** Keywords matching and optimization
- **Multi-template:** 8 professional templates
- **Language support:** English, French, Spanish, German, Italian, Portuguese, Arabic

## Development

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### API Testing

Use the Swagger UI at http://localhost:8000/docs

## Testing

Run a complete test flow:

1. **Upload CV:** POST `/api/upload/cv` with PDF file
2. **Create job:** POST `/api/jobs/paste` with job description
3. **Generate CV:** POST `/api/cv/generate` with CV ID and job ID
4. **Download:** GET `/api/cv/{id}/download`

Example with curl (when SKIP_AUTH=true):

```bash
# Get demo user ID
DEMO_USER="579fce1e-1604-4b00-b692-1f3b5ce43368"

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

# Generate CV (use IDs from previous responses)
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

### Docker issues

```bash
# Rebuild from scratch
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

### Database issues

```bash
# Reset database
docker compose down -v
docker compose up -d
```

### Logs

```bash
docker compose logs -f api
docker compose logs -f frontend
```

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues with VPS deployment, see [DEPLOYMENT.md](DEPLOYMENT.md)
