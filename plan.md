# CVBooster — Plan détaillé du projet

## Vision

Application full-stack (API + Frontend) qui permet à un utilisateur de :
1. Se connecter via Google, Facebook ou TikTok (OAuth)
2. Uploader son CV en PDF + fournir une annonce d'emploi (URL scrapée ou texte collé)
3. Recevoir un CV personnalisé, optimisé pour les ATS, dans un template moderne au choix

## Configuration choisie

| Décision | Choix |
|---|---|
| Backend/API | **FastAPI (Python)** — natif pour LiteParse, crawl4ai, LLM calls |
| Frontend | **Next.js 15 (App Router, React 19)** — SSR, excellent DX |
| Database & Auth | **Supabase** (PostgreSQL + Auth social Google/FB/TikTok) |
| LLM | **Flexible (OpenRouter)** — configurable, multi-modèles |
| PDF Generation | **WeasyPrint + Jinja2** côté backend (HTML/CSS → PDF) |
| PDF Parsing | **LiteParse** (pip install liteparse) — extraction rapide PDF |
| Web Scraping | **crawl4ai** (pip install -U crawl4ai) — scraping annonces |
| Templates CV | **8 templates** (Clean, Modern, Minimal, Corporate, Tech, Creative, Academic, Executive) |
| Job input | **URL + texte collé** — les deux options |
| Deployment | **Docker self-hosted (VPS)** — docker-compose pour API + Front |
| Pricing MVP | **100% gratuit** — open source |

---

## Architecture globale

```
┌─────────────────────────────────────────────────────────┐
│                      User (Browser)                     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   Frontend (Next.js 15)                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ │
│  │  Auth    │ │  Upload  │ │  Preview │ │  Download  │ │
│  │  Pages   │ │  CV + JD │ │  CV Gen  │ │  PDF       │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │          Template Selector (8 styles)              │ │
│  └────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────┘
                         │ REST/HTTP
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  API (FastAPI — Python)                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │  Auth    │ │  File    │ │  CV      │ │  Job     │   │
│  │  Proxy   │ │  Upload  │ │  Engine  │ │  Scraper │   │
│  │(Supabase)│ │(Storage) │ │(LLM+PDF) │ │(crawl4ai)│   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │              LiteParse (PDF extraction)           │   │
│  └──────────────────────────────────────────────────┘   │
└──────────┬──────────────────────┬───────────────────────┘
           │                      │
           ▼                      ▼
┌──────────────────┐  ┌──────────────────────────────────┐
│   Supabase       │  │       LLM Provider (OpenRouter)  │
│  ┌────────────┐  │  │  (GPT-4o / Claude / configurable)│
│  │ PostgreSQL │  │  └──────────────────────────────────┘
│  │  - users  │  │
│  │  - cvs    │  │  ┌──────────────────────────────────┐
│  │  - jobs   │  │  │  External Job Boards (scraping)   │
│  └────────────┘  │  │  (LinkedIn, Indeed, etc.)         │
│  ┌────────────┐  │  └──────────────────────────────────┘
│  │  Storage   │  │
│  │  - PDFs   │  │
│  └────────────┘  │
└──────────────────┘
```

---

## Stack technique détaillée

### Frontend — Next.js 15 (TypeScript)

```
packages:
  - next@15              # App Router, SSR/CSR hybrid
  - react@19             # React latest
  - @supabase/ssr        # Auth SSR pour Next.js
  - @supabase/supabase-js # Client Supabase
  - @tanstack/react-query # Data fetching/caching
  - tailwindcss          # Utility CSS
  - shadcn/ui            # Composants UI (accessible)
  - react-dropzone       # Drag & drop file upload
  - framer-motion        # Animations subtiles
  - zustand              # State management léger
  - axios                # HTTP client pour API
  - zod + @hookform/resolvers + react-hook-form # Form validation
```

### Backend — FastAPI (Python)

```
packages:
  - fastapi              # Framework API
  - uvicorn              # ASGI server
  - pydantic             # Validation de données
  - python-multipart     # File uploads
  - supabase             # Supabase Python client
  - litellm              # LLM abstraction (multi-provider)
  - liteparse            # PDF extraction rapide
  - crawl4ai             # Web scraping intelligent
  - weasyprint           # HTML/CSS → PDF generation
  - jinja2               # HTML templating
  - python-dotenv        # Environment variables
  - httpx                # HTTP client async
```

### Infrastructure

```
tools:
  - docker + docker-compose
  - nginx                # Reverse proxy
  - certbot              # SSL/TLS (Let's Encrypt)
  - supabase (cloud)     # Managed PostgreSQL + Auth + Storage
```

---

## Structure du projet

```
cvbooster/
├── docker-compose.yml
├── .env.example
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env
│   ├── pyproject.toml
│   └── src/
│       ├── __init__.py
│       ├── main.py                 # FastAPI app entry point
│       ├── config.py               # Settings (env vars)
│       ├── database.py             # Supabase client setup
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py             # Pydantic: User
│       │   ├── cv.py               # Pydantic: CV, CVTemplate
│       │   ├── job.py              # Pydantic: JobPosting
│       │   └── response.py         # Pydantic: API responses
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── auth.py             # Auth proxy endpoints
│       │   ├── upload.py           # CV upload + job posting
│       │   ├── cv_engine.py        # CV generation (LLM + PDF)
│       │   ├── scraper.py          # Job scraping (crawl4ai)
│       │   └── templates.py        # Template listing/selection
│       ├── services/
│       │   ├── __init__.py
│       │   ├── pdf_parser.py       # LiteParse: extract CV content
│       │   ├── job_scraper.py      # crawl4ai: scrape job URL
│       │   ├── llm_service.py      # LLM calls (litellm)
│       │   ├── ats_optimizer.py    # ATS keyword matching logic
│       │   ├── pdf_generator.py    # WeasyPrint: HTML→PDF
│       │   └── supabase_service.py # DB operations wrapper
│       ├── templates/              # Jinja2 HTML templates (CV styles)
│       │   ├── base.html
│       │   ├── clean.html
│       │   ├── modern.html
│       │   ├── minimal.html
│       │   ├── corporate.html
│       │   ├── tech.html
│       │   ├── creative.html
│       │   ├── academic.html
│       │   └── executive.html
│       ├── static/
│       │   └── styles/
│       │       ├── clean.css
│       │       ├── modern.css
│       │       ├── minimal.css
│       │       ├── corporate.css
│       │       ├── tech.css
│       │       ├── creative.css
│       │       ├── academic.css
│       │       └── executive.css
│       └── utils/
│           ├── __init__.py
│           ├── auth.py             # JWT verification, Supabase JWT
│           └── validators.py       # Input validation helpers
│
└── frontend/
    ├── Dockerfile
    ├── next.config.ts
    ├── tailwind.config.ts
    ├── tsconfig.json
    ├── .env.local
    ├── public/
    │   ├── templates/              # Preview thumbnails
    │   │   ├── clean.png
    │   │   ├── modern.png
    │   │   └── ...
    │   └── logos/
    └── src/
        ├── app/
        │   ├── layout.tsx          # Root layout (providers, nav)
        │   ├── page.tsx            # Landing page
        │   ├── login/
        │   │   └── page.tsx        # Login page (social auth buttons)
        │   ├── dashboard/
        │   │   ├── page.tsx        # Dashboard: history, new CV
        │   │   └── layout.tsx      # Authenticated layout (sidebar)
        │   ├── create/
        │   │   └── page.tsx        # Multi-step: upload → job → template → generate
        │   ├── preview/
        │   │   └── page.tsx        # Live preview + download
        │   └── api/
        │       └── auth/           # Next.js auth route handlers (Supabase SSR)
        ├── components/
        │   ├── ui/                 # shadcn/ui components
        │   ├── auth/
        │   │   ├── social-login.tsx       # Google/FB/TikTok buttons
        │   │   └── auth-provider.tsx      # Supabase context
        │   ├── cv/
        │   │   ├── upload-zone.tsx        # Drag & drop PDF upload
        │   │   ├── job-input.tsx          # URL input + textarea
        │   │   ├── template-grid.tsx      # Template selector (cards)
        │   │   ├── cv-preview.tsx         # PDF embed / iframe preview
        │   │   └── download-button.tsx    # Download generated PDF
        │   ├── layout/
        │   │   ├── header.tsx
        │   │   ├── sidebar.tsx
        │   │   └── footer.tsx
        │   └── common/
        │       ├── loading-spinner.tsx
        │       ├── error-banner.tsx
        │       └── step-indicator.tsx     # Multi-step wizard
        ├── lib/
        │   ├── supabase/
        │   │   ├── client.ts          # Browser client
        │   │   ├── server.ts          # Server client (RSC)
        │   │   └── middleware.ts      # Auth middleware
        │   ├── api-client.ts          # Axios instance for backend
        │   ├── constants.ts           # API URLs, template names
        │   └── utils.ts               # Helpers (cn, formatters)
        ├── hooks/
        │   ├── use-auth.ts            # Auth state + actions
        │   ├── use-cv-generation.ts   # CV generation flow
        │   └── use-file-upload.ts     # File upload with progress
        ├── store/
        │   └── cv-store.ts            # Zustand: CV creation state
        └── types/
            ├── user.ts
            ├── cv.ts
            └── job.ts
```

---

## Base de données — Supabase (PostgreSQL)

### Table `profiles` (étendue de `auth.users`)

```sql
CREATE TABLE profiles (
  id            UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name     TEXT,
  avatar_url    TEXT,
  provider      TEXT,           -- 'google', 'facebook', 'tiktok'
  created_at    TIMESTAMPTZ DEFAULT now(),
  updated_at    TIMESTAMPTZ DEFAULT now()
);

-- Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE USING (auth.uid() = id);
```

### Table `original_cvs`

```sql
CREATE TABLE original_cvs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  file_url      TEXT NOT NULL,         -- Supabase Storage URL
  file_name     TEXT,
  file_size     BIGINT,
  extracted_data JSONB,                -- Parsed CV content (from LiteParse)
  created_at    TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE original_cvs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users access own CVs"
  ON original_cvs FOR ALL USING (auth.uid() = user_id);
```

### Table `job_postings`

```sql
CREATE TABLE job_postings (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  source_url    TEXT,                  -- Original job URL (nullable)
  title         TEXT,
  company       TEXT,
  raw_content   TEXT,                  -- Scraped/pasted job description
  parsed_data   JSONB,                 -- Structured: skills, requirements, etc.
  created_at    TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE job_postings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users access own jobs"
  ON job_postings FOR ALL USING (auth.uid() = user_id);
```

### Table `generated_cvs`

```sql
CREATE TABLE generated_cvs (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  original_cv_id    UUID NOT NULL REFERENCES original_cvs(id) ON DELETE CASCADE,
  job_posting_id    UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
  template_name     TEXT NOT NULL,     -- 'clean', 'modern', etc.
  file_url          TEXT NOT NULL,     -- Supabase Storage URL (generated PDF)
  llm_output        JSONB,             -- Tailored content (JSON Resume format)
  ats_score         REAL,              -- Estimated ATS match score (0-100)
  keywords_matched  INTEGER,
  keywords_total    INTEGER,
  created_at        TIMESTAMPTZ DEFAULT now(),
  updated_at        TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE generated_cvs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users access own generated CVs"
  ON generated_cvs FOR ALL USING (auth.uid() = user_id);
```

### Supabase Storage Buckets

```
Bucket: "original-cvs"
  - {user_id}/{timestamp}_{filename}.pdf
  - Public: false (signed URLs)

Bucket: "generated-cvs"
  - {user_id}/{generated_cv_id}.pdf
  - Public: false (signed URLs)
```

---

## Flux utilisateur détaillé (User Journey)

### Étape 1 — Authentification

```
User visite l'app → Page d'accueil (landing)
  → Clique "Connexion" → Page login
    → Choix: Google | Facebook | TikTok
      → Redirection OAuth (Supabase gère le flow)
        → Callback → Session créée → Redirection /dashboard
```

Détails techniques :
- Supabase Auth gère Google et Facebook nativement
- TikTok nécessite un **Custom OAuth provider** dans Supabase (OAuth2 non-standard)
- Le middleware Next.js (`src/middleware.ts`) vérifie la session sur chaque route protégée
- Trigger Supabase `on_auth_user_created` crée automatiquement un `profile`

### Étape 2 — Upload du CV

```
Dashboard → Bouton "Créer un CV" → Page /create (step wizard)
  Step 1: Upload Zone
    → Drag & drop PDF ou clic pour parcourir
    → Validation: max 10MB, format PDF uniquement
    → Upload vers Supabase Storage → Appel API backend /parse-cv
      → Backend: LiteParse extrait le contenu textuel structuré
      → Sauvegarde dans `original_cvs` (file_url + extracted_data JSONB)
      → Retour: statut "CV analysé avec succès"
```

### Étape 3 — Annonce d'emploi

```
Step 2: Job Posting Input
  Option A: Coller l'URL
    → User colle l'URL (LinkedIn, Indeed, etc.)
    → Appel API backend /scrape-job?url=...
      → Backend: crawl4ai scrape la page, extrait la description
      → Sauvegarde dans `job_postings` (raw_content + parsed_data)
  Option B: Coller le texte
    → User colle le texte de l'annonce dans une textarea
    → Sauvegarde directement dans `job_postings`
  → Validation: titre + description détectés
    → Retour: résumé de l'annonce détectée (titre, entreprise, clés compétences)
```

### Étape 4 — Choix du template

```
Step 3: Template Selection
  → Grille de 8 templates avec preview thumbnail
  → Chaque card: nom + miniature + badge ATS-friendly
  → Clic → sélection visuelle (border highlight)
  → Templates disponibles:
    1. Clean      — Simple, élégant, beaucoup d'espace blanc
    2. Modern     — Design contemporain, accents de couleur
    3. Minimal    — Ultra-sobre, typographie uniquement
    4. Corporate  — Professionnel, deux colonnes légères
    5. Tech       — Orienté développement, section skills en avant
    6. Creative   — Design audacieux, couleurs vives
    7. Academic   — Style universitaire, publications en avant
    8. Executive  — Senior management, impact et leadership
```

### Étape 5 — Génération du CV

```
Step 4: Génération (Processing)
  → Clic "Générer mon CV"
  → Appel API backend /generate-cv avec:
    { original_cv_id, job_posting_id, template_name }

  Processus backend (asynchrone):

  1. RÉCUPÉRATION DES DONNÉES
     - Récupère le CV extrait (original_cvs.extracted_data)
     - Récupère l'annonce (job_postings.parsed_data)

  2. ANALYSE ATS (ATS Optimizer)
     - Extrait les mots-clés de l'annonce (skills, outils, soft skills)
     - Calcule le score de correspondance actuel (CV vs annonce)
     - Identifie les lacunes (keywords manquants)

  3. GÉNÉRATION LLM
     - Prompt à l'LLM (via litellm):
       "Tu es un expert en recrutement et optimisation ATS.
        Voici le CV original de l'utilisateur et l'annonce d'emploi.
        Récrit le CV pour maximiser la compatibilité ATS tout en restant
        honnête et professionnel. Utilise les mots-clés exacts de l'annonce.
        Retourne un objet JSON conformant au JSON Resume schema."
     - LLM retourne le CV restructuré en JSON

  4. GÉNÉRATION PDF
     - Charge le template Jinja2 correspondant
     - Rendu HTML avec les données du CV optimisé
     - WeasyPrint convertit HTML + CSS → PDF
     - Upload du PDF vers Supabase Storage
     - Sauvegarde dans `generated_cvs` (file_url + ats_score + llm_output)

  5. RÉPONSE
     - Retourne: { generated_cv_id, file_url, ats_score, preview_url }

  → Frontend: redirect vers /preview?id={generated_cv_id}
    → Affiche le PDF (iframe embed avec signed URL)
    → Affiche le score ATS (barre de progression)
    → Bouton "Télécharger PDF"
    → Bouton "Changer de template" (regénère avec autre style)
```

---

## API Endpoints (FastAPI)

### Authentification (proxy vers Supabase)

```
POST   /api/auth/callback          # Handle OAuth callback
GET    /api/auth/session           # Get current user session
POST   /api/auth/signout           # Sign out user
GET    /api/auth/profile           # Get user profile
PUT    /api/auth/profile           # Update user profile
```

### Upload & Parsing

```
POST   /api/upload/cv              # Upload PDF CV (multipart)
GET    /api/upload/cv/{cv_id}      # Get CV details + extracted data
GET    /api/upload/cvs             # List user's original CVs
DELETE /api/upload/cv/{cv_id}      # Delete original CV
```

### Job Postings

```
POST   /api/jobs/scrape            # Scrape job URL (crawl4ai)
POST   /api/jobs/paste             # Submit pasted job text
GET    /api/jobs/{job_id}          # Get job posting details
GET    /api/jobs                   # List user's job postings
DELETE /api/jobs/{job_id}          # Delete job posting
```

### CV Generation

```
POST   /api/cv/generate            # Generate tailored CV (LLM + PDF)
GET    /api/cv/{cv_id}             # Get generated CV details
GET    /api/cv/{cv_id}/download    # Download generated PDF
GET    /api/cv/{cv_id}/preview     # Get preview URL (signed)
GET    /api/cvs                    # List user's generated CVs
POST   /api/cv/{cv_id}/retail      # Regenerate with different template
DELETE /api/cv/{cv_id}             # Delete generated CV
```

### Templates

```
GET    /api/templates              # List all available templates
GET    /api/templates/{name}       # Get template details + preview
```

---

## Logique ATS — Détail du moteur d'optimisation

### Pipeline de scoring ATS

```
1. EXTRACTION DES MOTS-CLÉS (de l'annonce)
   ┌─────────────────────────────────────────────┐
   │ LLM analyse l'annonce et retourne:          │
   │ {                                           │
   │   "hard_skills": ["Python", "React", ...],  │
   │   "soft_skills": ["leadership", ...],       │
   │   "tools": ["Docker", "AWS", ...],          │
   │   "certifications": ["PMP", ...],           │
   │   "years_required": 5,                      │
   │   "education_level": "Bachelor"             │
   │ }                                           │
   └─────────────────────────────────────────────┘

2. ANALYSE DU CV ORIGINAL
   ┌─────────────────────────────────────────────┐
   │ Même structure pour le CV extrait:           │
   │ {                                           │
   │   "hard_skills": ["Python", "JavaScript"],  │
   │   "soft_skills": ["teamwork"],              │
   │   "tools": ["Git"],                         │
   │   "years_experience": 3,                    │
   │   "education": "Master"                     │
   │ }                                           │
   └─────────────────────────────────────────────┘

3. CALCUL DU SCORE
   - Keyword match rate: (matched / total) × 40%
   - Experience match: (years / required) × 20%
   - Education match: binary × 15%
   - Format compliance (ATS rules): × 15%
   - Contextual relevance (LLM judged): × 10%

4. OPTIMISATION (LLM prompt)
   - Intégration naturelle des mots-clés manquants
   - Reformulation des bullet points pour inclure les termes exacts
   - Structure standardisée (sections ATS-friendly)
   - Conservation de la véracité (pas de fabrication)
```

### Règles ATS respectées dans les templates

```
✓ Single-column layout (pas de colonnes complexes)
✓ Pas de tables, pas de text boxes
✓ Pas de graphiques, images décoratives, icônes
✓ En-têtes de section standards (Experience, Education, Skills)
✓ Font standard (Arial, Calibri, Helvetica)
✓ Marges standard (0.5" - 1")
✓ Bullet points simples
✓ PDF text-based (pas d'image scannée)
✓ Métadonnées PDF incluant les mots-clés
```

---

## LLM Prompt — Template de génération du CV

```python
SYSTEM_PROMPT = """
You are an expert resume writer and ATS optimization specialist.
Your task is to rewrite a candidate's resume to maximize its match
with a specific job description, while maintaining complete honesty.

RULES:
1. Use EXACT keywords from the job description (verbatim match)
2. Never fabricate experience, skills, or achievements
3. Rephrase existing experience to highlight relevant aspects
4. Use standard section headers: Experience, Education, Skills, Summary
5. Keep it to 1-2 pages maximum
6. Use quantifiable achievements where possible
7. Output must be valid JSON matching the JSON Resume schema
   (https://jsonresume.org/schema/)
"""

USER_PROMPT_TEMPLATE = """
Original Resume (extracted):
{original_cv_data}

Job Description:
{job_posting_data}

Key ATS Keywords to include:
{ats_keywords}

Please rewrite the resume to maximize ATS compatibility.
Return ONLY valid JSON in the JSON Resume format.
"""
```

---

## Templates CV — Spécifications

Chaque template est composé de :
- **Un fichier Jinja2 HTML** (`backend/src/templates/{name}.html`)
- **Un fichier CSS dédié** (`backend/src/static/styles/{name}.css`)
- **Une miniature PNG** (`frontend/public/templates/{name}.png`)

### Spécifications par template

| Template | Style | Couleur dominante | Meilleur pour |
|---|---|---|---|
| **Clean** | Blanc, lignes fines | Gris foncé | Tous secteurs |
| **Modern** | Accents de couleur, géométrie | Bleu | Tech, Marketing |
| **Minimal** | Typo-only, pas de couleur | Noir | Design, Architecture |
| **Corporate** | Double colonne légère | Bleu marine | Finance, Consulting |
| **Tech** | Code-font headers, skills bar | Vert/Noir | Développeur, Data |
| **Creative** | Couleurs vives, asymétrie | Orange/Violet | Marketing, Design |
| **Academic** | Sections publications | Bordeaux | Recherche, Académie |
| **Executive** | Impact, chiffres clés | Gris anthracite | C-Level, Management |

Tous les templates respectent les règles ATS listées ci-dessus.

---

## TikTok OAuth — Configuration spécifique

TikTok utilise un OAuth2 non-standard. Configuration dans Supabase :

```
Dans le Dashboard Supabase → Authentication → Providers → Custom OAuth:

Name:              tiktok
Client ID:         {TikTok API Key}
Client Secret:     {TikTok API Secret}
Authorize URL:     https://www.tiktok.com/v2/auth/authorize/
Token URL:         https://open.tiktokapis.com/v2/oauth/token/
User Info URL:     https://open.tiktokapis.com/v2/user/info/
Redirect URL:      {YOUR_APP_URL}/auth/callback
Scope:             user.basic.profile

Note: TikTok nécessite l'application d'être approuvée via le
TikTok Developer Portal avant de pouvoir être utilisée en production.
Pour le développement, utilisez le mode sandbox.
```

---

## Docker — docker-compose.yml

```yaml
version: '3.9'

services:
  # Backend API
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend:/app
    depends_on:
      - crawl4ai

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    env_file:
      - ./frontend/.env.local
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - api

  # Nginx (Reverse Proxy)
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - api
      - frontend
```

---

## Plan de développement — Phases

### Phase 1 — Fondations (Semaine 1-2)

```
□ Initialiser le projet (structure de dossiers, git)
□ Configurer Supabase (project, tables, RLS, storage buckets)
□ Configurer OAuth Google + Facebook dans Supabase
□ Configurer Custom OAuth TikTok dans Supabase
□ Crée le backend FastAPI (main.py, config.py, database.py)
□ Implémente les Pydantic models (user, cv, job, response)
□ Crée le frontend Next.js (initial setup, Tailwind, shadcn/ui)
□ Implémente le middleware auth Next.js + Supabase SSR
□ Configure Docker + docker-compose
□ Tests: auth flow Google, Facebook, TikTok
```

### Phase 2 — Upload & Parsing CV (Semaine 3-4)

```
□ Implémente Supabase Storage upload (backend + frontend)
□ Intègre LiteParse pour l'extraction PDF
□ Crée le endpoint /api/upload/cv
□ Crée le composant UploadZone (drag & drop, validation)
□ Stocke les données extraites dans `original_cvs` (JSONB)
□ Tests: upload CV PDF → extraction → vérification données
```

### Phase 3 — Scraping des annonces (Semaine 5)

```
□ Intègre crawl4ai pour le scraping web
□ Crée le endpoint /api/jobs/scrape
□ Crée le endpoint /api/jobs/paste
□ Crée le composant JobInput (URL + textarea, tabs)
□ Parse et structure les données d'annonce (JSONB)
□ Tests: scrape LinkedIn/Indeed → extraction → vérification
```

### Phase 4 — Moteur ATS + LLM (Semaine 6-7)

```
□ Implémente le service ATS Optimizer (keyword extraction, scoring)
□ Configure litellm avec OpenRouter (multi-provider)
□ Crée le service LLM (prompt engineering, JSON output)
□ Implémente le prompt de génération du CV
□ Crée le endpoint /api/cv/generate
□ Pipeline complet: CV + annonce → LLM → CV optimisé (JSON)
□ Tests: pipeline end-to-end → score ATS → vérification contenu
```

### Phase 5 — Templates + PDF Generation (Semaine 8-9)

```
□ Crée les 8 templates Jinja2 HTML
□ Crée les 8 fichiers CSS correspondants
□ Génère les miniatures PNG pour chaque template
□ Intègre WeasyPrint pour HTML → PDF
□ Crée le service PDF Generator
□ Crée le composant TemplateGrid (sélection visuelle)
□ Crée le composant CVPreview (iframe embed)
□ Crée le composant DownloadButton
□ Tests: chaque template → rendu PDF → vérification visuelle
```

### Phase 6 — UI/UX + Polish (Semaine 10-11)

```
□ Page Landing (hero, features, CTA)
□ Dashboard (liste CV générés, stats, nouveau CV)
□ Wizard multi-étapes (step indicator, navigation)
□ Score ATS affiché (barre de progression, détails)
□ Regénérer avec un autre template
□ Historique des CVs (liste avec filtres)
□ Responsive design (mobile, tablet, desktop)
□ Animations (Framer Motion)
□ Error handling + messages utilisateur
□ Tests: parcours utilisateur complet
```

### Phase 7 — Déploiement + Documentation (Semaine 12)

```
□ Optimise les Dockerfiles (multi-stage build)
□ Configure Nginx + SSL (certbot)
□ Script de déploiement sur VPS
□ README.md complet (setup, dev, deploy)
□ .env.example avec toutes les variables
□ Documentation API (OpenAPI/Swagger auto-généré par FastAPI)
□ Monitoring basique (logs, health checks)
□ Tests de charge basiques
□ Déploiement en production
```

---

## Variables d'environnement

### Backend (.env)

```env
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=svc...

# LLM (OpenRouter via litellm)
OPENROUTER_API_KEY=sk-or-...
LLM_MODEL=openai/gpt-4o

# App
APP_NAME=CVBooster
APP_ENV=development
CORS_ORIGINS=http://localhost:3000,http://localhost:80
```

### Frontend (.env.local)

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Dépendances principales

### Backend — requirements.txt

```
fastapi==0.115.*
uvicorn[standard]==0.34.*
pydantic==2.*
python-multipart==0.0.*
supabase==2.*
litellm==1.*
liteparse==0.*
crawl4ai==0.*
weasyprint==6.*
jinja2==3.*
python-dotenv==1.*
httpx==0.28.*
```

### Frontend — package.json (dépendances clés)

```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@supabase/ssr": "^0.5.*",
    "@supabase/supabase-js": "^2.*",
    "@tanstack/react-query": "^5.*",
    "tailwindcss": "^3.4.*",
    "react-dropzone": "^14.*",
    "framer-motion": "^11.*",
    "zustand": "^5.*",
    "axios": "^1.*",
    "zod": "^3.*",
    "react-hook-form": "^7.*",
    "@hookform/resolvers": "^3.*"
  }
}
```

---

## Risques et Points d'attention

| Risque | Impact | Atténuation |
|---|---|---|
| TikTok OAuth approuvé | Moyen | Commencer avec Google+FB, ajouter TikTok après approbation |
| Coût LLM (OpenRouter) | Moyen | Limiter à 5 CV/jour par utilisateur en MVP |
| crawl4ai bloqué par les sites | Moyen | Implémenter fallback: texte collé toujours disponible |
| Qualité des templates PDF | Moyen | Test manuel exhaustif de chaque template |
| LiteParse mal extrait certains PDF | Faible | Fallback: permettre l'édition manuelle du CV extrait |
| Timeout génération CV | Moyen | Implémenter queue de tâches (Celery/ARQ) si besoin |

---

## Métriques de succès MVP

- [ ] Utilisateur peut se connecter avec Google sans friction
- [ ] PDF upload + extraction fonctionne pour 90% des CV standards
- [ ] Scraping fonctionne pour LinkedIn, Indeed, Glassdoor
- [ ] CV généré passe un test ATS (score > 75/100)
- [ ] Les 8 templates produisent un PDF lisible et professionnel
- [ ] Temps de génération < 30 secondes
- [ ] Application responsive (mobile + desktop)

---

## Prochaines étapes immédiates

1. **Créer le projet git** et initialiser la structure de dossiers
2. **Configurer Supabase** (project, auth providers, tables)
3. **Bootstrapper le backend FastAPI** (Dockerfile + requirements)
4. **Bootstrapper le frontend Next.js** (Tailwind + shadcn/ui)
5. **Implémenter l'authentification Google** (premier provider)
