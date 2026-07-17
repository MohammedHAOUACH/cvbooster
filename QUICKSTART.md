# Quick Start - CVBooster VPS

## Installation Rapide (5 minutes)

```bash
# 1. Cloner
cd ~ && git clone <repo> && cd cvbooster

# 2. Initialiser
./scripts/init.sh

# 3. Configurer .env
nano .env
# Remplir: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, OPENROUTER_API_KEY

# 4. Déployer
docker compose up -d --build

# 5. Accéder
open http://localhost
```

## Commandes Utiles

```bash
# Voir les logs
docker compose logs -f api
docker compose logs -f frontend

# Arrêter
docker compose down

# Redémarrer
docker compose restart

# Mettre à jour
git pull && docker compose down && docker compose up -d --build

# Backup base de données
docker run --rm -v cvbooster_sqlite-data:/data -v $(pwd)/backup:/backup alpine cp /data/cvbooster.db /backup/

# Tester API
curl http://localhost/health
```

## Configuration Requise

1. **Google OAuth** (https://console.cloud.google.com/)
   - Client ID
   - Client Secret
   - Redirect URI: `http://vps-ip/api/auth/google/callback`

2. **OpenRouter** (https://openrouter.ai/)
   - API Key (gratuit)

## Coût

- VPS: 5€/mois
- OpenRouter: Gratuit
- **Total: 5€/mois**

## Documentation Complète

- `DEPLOYMENT.md` - Guide complet de déploiement
- `VPS-DEPLOYMENT-CHECKLIST.md` - Checklist étape par étape
- `IMPLEMENTATION-SUMMARY.md` - Détails techniques
- `README.md` - Documentation générale
