# Plan de Déploiement VPS - CVBooster

## Objectif
Déployer CVBooster sur un petit VPS (1-2 Go RAM) avec:
- SQLite au lieu de Supabase (base de données locale)
- Authentification Google OAuth simple
- Modèle OpenRouter gratuit: tencent/hy3:free
- Docker Compose pour l'orchestration

## Architecture Cible

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Nginx     │────▶│   Backend    │────▶│   SQLite    │
│   Port 80   │     │  FastAPI     │     │   Local     │
└─────────────┘     └──────────────┘     └─────────────┘
       │                    │
       │                    ▼
       │             ┌──────────────┐
       └────────────▶│   Frontend   │
                     │  Next.js     │
                     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  OpenRouter  │
                     │  tencent/hy3 │
                     └──────────────┘
```

## Tâches Détaillées

### Phase 1: Base de données SQLite

#### 1.1 Créer service SQLite pour le backend
- Fichier: `backend/src/database.py`
- Utiliser SQLAlchemy avec SQLite
- Tables: profiles, original_cvs, job_postings, generated_cvs
- Initialisation automatique des tables au démarrage

```python
# Structure requise
from sqlalchemy import create_engine, Column, String, Text, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlite3

DATABASE_URL = "sqlite:///./cvbooster.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models SQLAlchemy correspondant aux tables Supabase
```

#### 1.2 Migrer LocalStorage vers SQLiteStorage
- Fichier: `backend/src/services/sqlite_storage.py`
- Remplacer `local_storage.py` par une implémentation SQLite persistante
- Méthodes: insert, get, list_by_user, update, delete

### Phase 2: Authentification Google OAuth

#### 2.1 Installer dépendances
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

#### 2.2 Créer service d'authentification Google
- Fichier: `backend/src/services/google_auth.py`
- Configurer OAuth 2.0 avec Google
- Créer endpoints:
  - `/api/auth/google` - Redirection vers Google
  - `/api/auth/google/callback` - Callback après authentification
- Stocker user info dans table profiles
- Générer JWT token simple pour les sessions

```python
# Variables d'environnement requises
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REDIRECT_URI=http://vps-ip/api/auth/google/callback
JWT_SECRET=xxx
```

#### 2.3 Mettre à jour utils/auth.py
- Ajouter vérification JWT personnalisée
- Modifier `get_current_user_id` pour supporter JWT local ET Supabase

### Phase 3: Configuration OpenRouter

#### 3.1 Mettre à jour llm_service.py
- Remplacer configuration locale par OpenRouter
- Utiliser modèle: `tencent/hy3:free`
- Configurer via litellm

```python
# Configuration OpenRouter
response = await acompletion(
    model="openrouter/tencent/hy3:free",
    messages=[...],
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    temperature=0.3,
    timeout=120,  # Modèles gratuits peuvent être lents
)
```

#### 3.2 Mettre à jour .env.example
```env
OPENROUTER_API_KEY=sk-or-xxx
USE_OPENROUTER=true
```

### Phase 4: Docker Compose

#### 4.1 Mettre à jour docker-compose.yml
- Ajouter volume persistant pour SQLite
- Ajouter volume pour uploads
- Configurer variables d'environnement

```yaml
services:
  api:
    volumes:
      - sqlite-data:/app/data
      - ./uploads:/app/uploads
  
  frontend:
    environment:
      - NEXT_PUBLIC_API_URL=/api
      - NEXT_PUBLIC_AUTH_PROVIDER=google
  
volumes:
  sqlite-data:
  uploads:
```

#### 4.2 Mettre à jour Dockerfile backend
- Ajouter création répertoire data
- S'assurer que SQLite peut écrire

### Phase 5: Frontend - Authentification Google

#### 5.1 Créer page de connexion Google
- Fichier: `frontend/src/app/login/page.tsx`
- Bouton "Se connecter avec Google"
- Redirection vers `/api/auth/google`

#### 5.2 Mettre à jour API client
- Fichier: `frontend/src/lib/api-client.ts`
- Gérer JWT token local (localStorage)
- Ajouter header Authorization automatique

#### 5.3 Supprimer dépendance Supabase
- Remplacer client Supabase par appel API direct
- Mettre à jour tous les composants utilisant Supabase

### Phase 6: nginx Configuration

#### 6.1 Mettre à jour nginx.conf
- Router `/api` vers backend
- Router `/auth` vers backend (pour OAuth callback)
- Router `/` vers frontend

### Phase 7: Scripts de déploiement

#### 7.1 Créer script d'initialisation
- Fichier: `scripts/init.sh`
- Créer répertoires
- Initialiser base de données
- Générer JWT_SECRET

#### 7.2 Créer documentation de déploiement VPS
- Fichier: `DEPLOYMENT.md`
- Étapes pour déployer sur VPS (Hetzner, DigitalOcean, OVH)
- Configuration firewall (ports 80, 443)
- Optionnel: SSL avec Let's Encrypt

## Variables d'Environnement Finales

```env
# App
APP_NAME=CVBooster
APP_ENV=production
CORS_ORIGINS=http://vps-ip
DEBUG=false
SKIP_AUTH=false

# Authentification Google
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REDIRECT_URI=http://vps-ip/api/auth/google/callback
JWT_SECRET=xxx

# OpenRouter
OPENROUTER_API_KEY=sk-or-xxx
USE_OPENROUTER=true

# Base de données
DATABASE_PATH=/app/data/cvbooster.db

# Uploads
UPLOADS_DIR=/app/uploads
```

## Tests Requis

### Test 1: Authentification
```bash
# Tester connexion Google
curl -v http://localhost/api/auth/google
# Vérifier callback et création user
```

### Test 2: Upload CV
```bash
#Uploader un CV PDF
curl -X POST http://localhost/api/upload/cv \
  -F "file=@chemin/vers/cv.pdf" \
  -H "Authorization: Bearer xxx"
```

### Test 3: Job Posting
```bash
# Créer job posting
curl -X POST http://localhost/api/jobs/paste \
  -H "Authorization: Bearer xxx" \
  -H "Content-Type: application/json" \
  -d '{"title":"Developer","raw_content":"..."}'
```

### Test 4: Génération CV
```bash
# Générer CV optimisé
curl -X POST http://localhost/api/cv/generate \
  -H "Authorization: Bearer xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "original_cv_id":"xxx",
    "job_posting_id":"yyy",
    "template_name":"clean"
  }'
```

### Test 5: LLM OpenRouter
```bash
# Vérifier que tencent/hy3:free répond
python3 -c "
import asyncio
from litellm import acompletion
async def test():
    response = await acompletion(
        model='openrouter/tencent/hy3:free',
        messages=[{'role':'user','content':'Hello'}],
        api_key='sk-or-xxx'
    )
    print(response.choices[0].message.content)
asyncio.run(test())
"
```

## Estimation Temps

| Tâche | Durée estimée |
|-------|---------------|
| SQLite storage | 30 min |
| Google OAuth backend | 45 min |
| Configuration OpenRouter | 15 min |
| Docker Compose | 20 min |
| Frontend auth | 40 min |
| nginx config | 15 min |
| Tests & débogage | 60 min |
| **Total** | **~4 heures** |

## Risques et Solutions

### Risque 1: Modèle tencent/hy3:free trop lent ou indisponible
**Solution:** Prévoir fallback vers autre modèle gratuit ou configurer queue

### Risque 2: Google OAuth callback URL doit être exacte
**Solution:** Utiliser variable d'environnement, documenter configuration Google Cloud Console

### Risque 3: SQLite concurrent access en production
**Solution:** Configurer correctement connection pooling, vérifier performance

### Risque 4: Frontend dépendant de Supabase
**Solution:** Refactoriser progressivement, tester chaque composant

## Commandes de Déploiement Finales

```bash
# 1. Cloner sur VPS
git clone <repo>
cd cvbooster

# 2. Configurer .env
cp .env.example .env
# Éditer .env avec les vraies valeurs

# 3. Lancer Docker
docker compose up -d --build

# 4. Vérifier
docker compose logs -f api
docker compose logs -f frontend

# 5. Tester navigateur
open http://vps-ip
```

## Prochaines Étapes (Optionnel)

1. Ajouter SSL avec Let's Encrypt (certbot)
2. Configurer domaine personnalisé
3. Ajouter backup automatique SQLite
4. Monitoring (simple health check)
5. Rate limiting pour API
6. Email notifications (généré CV prêt)
