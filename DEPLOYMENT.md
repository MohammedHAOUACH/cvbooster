# Déploiement CVBooster sur VPS

Ce guide explique comment déployer CVBooster sur un petit VPS (1-2 Go RAM) avec SQLite, authentification Google et le modèle gratuit OpenRouter.

## Architecture

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

## Prérequis

- VPS avec Ubuntu 22.04+ (1-2 Go RAM minimum)
- Docker et Docker Compose installés
- Compte Google Cloud (pour OAuth)
- Compte OpenRouter (pour API LLM gratuite)

## Installation Docker

```bash
# Installer Docker
sudo apt update
sudo apt install -y ca-certificates curl gnupg

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Tester Docker
sudo docker run hello-world
```

## Configuration Google OAuth

1. **Créer un projet Google Cloud**
   - Aller à https://console.cloud.google.com/
   - Créer un nouveau projet "CVBooster"
   - Sélectionner le projet

2. **Activer Google+ API**
   - Dans le menu: APIs et services > Bibliothèque
   - Rechercher "Google+ API"
   - Cliquer sur Activer

3. **Créer credentials OAuth**
   - APIs et services > Credentials
   - Créer des credentials > ID client OAuth
   - Type d'application: Application Web
   - Nom: CVBooster

4. **Configurer URI de redirection**
   - URI de redirection autorisés: `http://your-vps-ip/api/auth/google/callback`
   - Exemple: `http://123.45.67.89/api/auth/google/callback`
   - Sauvegarder

5. **Noter les credentials**
   - Client ID: `xxx.apps.googleusercontent.com`
   - Client Secret: `GOCSPX-xxx`

## Configuration OpenRouter

1. **Créer un compte**
   - Aller à https://openrouter.ai/
   - S'inscrire (gratuit)

2. **Obtenir une clé API**
   - Aller à https://openrouter.ai/keys
   - Créer une nouvelle clé
   - Noter la clé (commence par `sk-or-`)

3. **Modèle gratuit**
   - Modèle utilisé: `tencent/hy3:free`
   - Gratuit mais peut être lent
   - Limites: ~1000 requêtes/jour

## Déploiement sur VPS

### 1. Cloner le projet

```bash
cd ~
git clone https://github.com/votre-repo/cvbooster.git
cd cvbooster
```

### 2. Initialiser

```bash
chmod +x scripts/init.sh
./scripts/init.sh
```

### 3. Configurer .env

```bash
nano .env
```

Remplir avec vos credentials:

```env
# Google OAuth
GOOGLE_CLIENT_ID=votre-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=votre-client-secret
GOOGLE_REDIRECT_URI=http://votre-vps-ip/api/auth/google/callback

# OpenRouter
OPENROUTER_API_KEY=sk-or-votre-cle
USE_OPENROUTER=true

# JWT Secret (déjà généré par init.sh)
JWT_SECRET=xxx
```

### 4. Lancer Docker

```bash
docker compose up -d --build
```

### 5. Vérifier

```bash
# Voir les logs
docker compose logs -f api
docker compose logs -f frontend

# Vérifier les services
docker compose ps

# Tester l'API
curl http://localhost/health
```

### 6. Accéder à l'application

Ouvrir le navigateur: `http://votre-vps-ip`

## Configuration Firewall

```bash
# Ouvrir port HTTP (si UFW activé)
sudo ufw allow 80/tcp

# Si HTTPS avec Let's Encrypt
sudo ufw allow 443/tcp

# Activer UFW
sudo ufw enable

# Vérifier
sudo ufw status
```

## Maintenance

### Arrêter les services

```bash
docker compose down
```

### Redémarrer

```bash
docker compose restart
```

### Mettre à jour après git pull

```bash
git pull
docker compose down
docker compose up -d --build
```

### Voir les logs

```bash
# Tous les logs
docker compose logs

# Logs en temps réel
docker compose logs -f

# Logs API seulement
docker compose logs -f api

# Logs frontend seulement
docker compose logs -f frontend
```

### Backup de la base de données

```bash
# La base SQLite est dans le volume Docker
# Trouver le volume
docker volume ls | grep sqlite-data

# Backup manuel
docker run --rm \
  -v cvbooster_sqlite-data:/data \
  -v $(pwd)/backups:/backup \
  alpine cp /data/cvbooster.db /backup/cvbooster-$(date +%Y%m%d).db
```

### Backup des uploads

```bash
tar -czf backups/uploads-$(date +%Y%m%d).tar.gz uploads/
```

## Dépannage

### Problème: Google OAuth échoue

**Symptôme:** Redirection vers `/login?error=auth_failed`

**Solutions:**
1. Vérifier que `GOOGLE_REDIRECT_URI` dans .env correspond EXACTEMENT à l'URI configurée dans Google Cloud Console
2. Vérifier que Google+ API est activée
3. Vérifier les logs: `docker compose logs api`
4. S'assurer que le VPS est accessible depuis internet (pas localhost)

### Problème: OpenRouter trop lent ou échoue

**Symptôme:** Timeout lors de la génération CV

**Solutions:**
1. Vérifier la clé API: `echo $OPENROUTER_API_KEY`
2. Tester manuellement:
   ```bash
   curl -H "Authorization: Bearer sk-or-xxx" \
     https://openrouter.ai/api/v1/chat/completions \
     -d '{"model":"tencent/hy3:free","messages":[{"role":"user","content":"Hello"}]}'
   ```
3. Augmenter timeout dans nginx.conf (déjà à 600s)
4. Fallback vers local LLM si disponible

### Problème: Docker ne démarre pas

**Symptôme:** `docker compose up` échoue

**Solutions:**
```bash
# Vérifier Docker
sudo systemctl status docker

# Rebuild images
docker compose build --no-cache

# Supprimer et recréer
docker compose down -v
docker compose up -d --build

# Voir les logs d'erreur
docker compose logs
```

### Problème: Base de données corrompue

**Symptôme:** Erreurs SQLite

**Solutions:**
```bash
# Arrêter les services
docker compose down

# Supprimer le volume
docker volume rm cvbooster_sqlite-data

# Recréer
docker compose up -d
```

## Optionnel: HTTPS avec Let's Encrypt

```bash
# Installer certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir certificat (remplacez par votre email)
sudo certbot --nginx -d votre-domaine.com

# Renouvellement automatique (déjà configuré par certbot)
sudo certbot renew --dry-run
```

## Coûts

- **VPS:** ~5€/mois (Hetzner CX11, DigitalOcean Droplet 1Go)
- **OpenRouter:** Gratuit (tencent/hy3:free)
- **Google OAuth:** Gratuit
- **SQLite:** Gratuit

**Total: ~5€/mois**

## Limitations

1. **Modèle gratuit:** tencent/hy3:free peut être lent ou indisponible
2. **SQLite:** Pas idéal pour haute concurrence (OK pour < 100 utilisateurs)
3. **Pas de backup automatique:** À configurer manuellement
4. **Pas de monitoring:** Ajouter si nécessaire (Prometheus, Grafana)

## Prochaines améliorations

1. [ ] Ajouter backup automatique quotidien
2. [ ] Configurer HTTPS avec Let's Encrypt
3. [ ] Ajouter monitoring simple (health checks)
4. [ ] Configurer domaine personnalisé
5. [ ] Ajouter rate limiting API
6. [ ] Email notifications (CV généré prêt)
7. [ ] Fallback vers plusieurs modèles OpenRouter

## Support

En cas de problème:
1. Vérifier les logs: `docker compose logs -f`
2. Consulter ce guide de dépannage
3. Vérifier la configuration .env
4. Tester chaque service séparément
