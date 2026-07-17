# Checklist Déploiement VPS - CVBooster

## Avant le Déploiement

### 1. VPS Preparation
- [ ] VPS provisionné (minimum 1Go RAM, recommandé 2Go)
- [ ] Ubuntu 22.04+ installé
- [ ] SSH configuré (clé SSH recommandée)
- [ ] Firewall configuré (port 22, 80, 443)
- [ ] Swap configuré (si 1Go RAM: 2Go swap)

### 2. Docker Installation
- [ ] Docker installé
- [ ] Docker Compose installé
- [ ] Test: `docker run hello-world`

### 3. Google OAuth Configuration
- [ ] Compte Google Cloud créé
- [ ] Projet "CVBooster" créé
- [ ] Google+ API activée
- [ ] Credentials OAuth 2.0 créés
- [ ] URI de redirection configurée: `http://vps-ip/api/auth/google/callback`
- [ ] Client ID noté
- [ ] Client Secret noté

### 4. OpenRouter Configuration
- [ ] Compte OpenRouter créé (https://openrouter.ai/)
- [ ] Clé API générée
- [ ] Clé API notée (sk-or-xxx)

## Déploiement

### 1. Cloner et Initialiser
```bash
[ ] cd ~
[ ] git clone <repo>
[ ] cd cvbooster
[ ] chmod +x scripts/*.sh
[ ] ./scripts/init.sh
```

### 2. Configurer .env
```bash
[ ] nano .env
[ ] Remplir GOOGLE_CLIENT_ID
[ ] Remplir GOOGLE_CLIENT_SECRET
[ ] Remplir GOOGLE_REDIRECT_URI (avec IP VPS réelle)
[ ] JWT_SECRET déjà généré (ne pas changer)
[ ] Remplir OPENROUTER_API_KEY
[ ] Vérifier USE_OPENROUTER=true
[ ] Sauvegarder (Ctrl+O, Ctrl+X)
```

### 3. Vérifier Configuration
```bash
[ ] ./scripts/test-deployment.sh
[ ] Tous les checks doivent être ✓
```

### 4. Build et Lancement
```bash
[ ] docker compose build
[ ] Attendre la fin du build (~5-10 min)
[ ] docker compose up -d
[ ] docker compose ps (tous les services doivent être "up")
```

### 5. Vérifier Services
```bash
[ ] docker compose logs api | grep "Starting CVBooster"
[ ] docker compose logs api | grep "SQLite initialized"
[ ] docker compose logs frontend | grep "compiled ready"
[ ] curl http://localhost/health
[ ] Réponse: {"status":"ok","app":"CVBooster"}
```

### 6. Tester Authentification
```bash
[ ] Ouvrir navigateur: http://vps-ip
[ ] Cliquer "Se connecter avec Google"
[ ] Autoriser l'accès Google
[ ] Redirection vers l'application
[ ] Voir le nom de l'utilisateur
```

### 7. Tester Fonctionnalités Complètes
```bash
[ ] Uploader un CV PDF (fichier test disponible: exemple/CV Mohammed HAOUACH.pdf)
[ ] Créer un job posting (copier-coller description)
[ ] Générer un CV optimisé
[ ] Attendre la génération (peut prendre 1-2 min avec modèle gratuit)
[ ] Télécharger le CV généré
[ ] Vérifier le PDF est correct
```

## Post-Déploiement

### 1. Firewall
```bash
[ ] sudo ufw allow 80/tcp (si pas déjà fait)
[ ] sudo ufw allow 443/tcp (si HTTPS)
[ ] sudo ufw status
```

### 2. Backup Configuration
```bash
# Créer script de backup
[ ] nano /home/user/cvbooster-backup.sh

#!/bin/bash
cd /home/user/cvbooster
docker run --rm \
  -v cvbooster_sqlite-data:/data \
  -v $(pwd)/backups:/backup \
  alpine cp /data/cvbooster.db /backup/cvbooster-$(date +%Y%m%d).db
tar -czf /backup/uploads-$(date +%Y%m%d).tar.gz uploads/

# Ajouter au cron
[ ] crontab -e
[ ] Ajouter: 0 2 * * * /home/user/cvbooster-backup.sh
```

### 3. Monitoring (Optionnel)
```bash
# Créer script de health check
[ ] nano /home/user/cvbooster-health.sh

#!/bin/bash
if ! curl -f http://localhost/health > /dev/null 2>&1; then
  echo "CVBooster down - restarting"
  docker compose restart
fi

# Ajouter au cron
[ ] crontab -e
[ ] Ajouter: */5 * * * * /home/user/cvbooster-health.sh
```

### 4. HTTPS avec Let's Encrypt (Recommandé)
```bash
[ ] sudo apt install certbot python3-certbot-nginx
[ ] sudo certbot --nginx -d votre-domaine.com
[ ] Suivre les instructions
[ ] Tester: https://votre-domaine.com
```

## Maintenance Régulière

### Hebdomadaire
- [ ] Vérifier les logs: `docker compose logs --tail=100 api`
- [ ] Vérifier l'espace disque: `df -h`
- [ ] Vérifier les backups existent

### Mensuel
- [ ] Mettre à jour Docker: `sudo apt update && sudo apt upgrade docker-ce`
- [ ] Mettre à jour l'application: `git pull && docker compose down && docker compose up -d --build`
- [ ] Renouveler certificats SSL: `sudo certbot renew --dry-run`

## Dépannage Rapide

### Service ne démarre pas
```bash
[ ] docker compose logs api
[ ] docker compose logs frontend
[ ] Vérifier .env (surtout GOOGLE_REDIRECT_URI)
[ ] docker compose down -v
[ ] docker compose up -d --build
```

### Google OAuth échoue
```bash
[ ] Vérifier GOOGLE_REDIRECT_URI dans .env
[ ] Vérifier URI dans Google Cloud Console (DOIT être identique)
[ ] Vérifier Google+ API activée
[ ] docker compose logs api | grep "Google"
```

### OpenRouter trop lent/échoue
```bash
[ ] Vérifier OPENROUTER_API_KEY
[ ] Tester: curl https://openrouter.ai/api/v1/chat/completions...
[ ] Vérifier les quotas OpenRouter
[ ] Option: installer local LLM (llama.cpp)
```

### Base de données corrompue
```bash
[ ] docker compose down
[ ] docker volume rm cvbooster_sqlite-data
[ ] docker compose up -d
[ ] Les utilisateurs doivent se reconnecter
```

## Coûts à Surveiller

- [ ] VPS: ~5€/mois
- [ ] OpenRouter: Gratuit (mais surveiller les quotas)
- [ ] Google OAuth: Gratuit
- [ ] Domaine: ~10€/an (optionnel)
- [ ] SSL: Gratuit (Let's Encrypt)

**Total mensuel: ~5-6€**

## Sécurité

### À Faire
- [ ] Changer JWT_SECRET par une valeur aléatoire forte
- [ ] Désactiver SKIP_AUTH (mettre à false)
- [ ] Configurer HTTPS (Let's Encrypt)
- [ ] Mettre à jour Docker régulièrement
- [ ] Backup régulier configuré
- [ ] SSH avec clé (pas de mot de passe)
- [ ] Firewall configuré

### À Éviter
- [x] Commiter .env avec vraies clés
- [x] Laisser SKIP_AUTH=true en production
- [x] Exposer port 8000 directement (passer par nginx)
- [x] Utiliser root pour Docker

## Checklist Finale

- [ ] Tous les services up
- [ ] Authentification Google fonctionne
- [ ] Upload CV fonctionne
- [ ] Génération CV fonctionne
- [ ] Download PDF fonctionne
- [ ] Backup configuré
- [ ] Monitoring configuré (optionnel)
- [ ] HTTPS configuré (recommandé)
- [ ] Documentation lue et comprise
- [ ] Clés API sécurisées

## Contacts / Ressources

- **Documentation:** DEPLOYMENT.md, IMPLEMENTATION-SUMMARY.md
- **Support Docker:** https://docs.docker.com/
- **Support Google OAuth:** https://developers.google.com/identity/protocols/oauth2
- **Support OpenRouter:** https://openrouter.ai/docs
- **Logs:** `docker compose logs -f`

---

**Date de déploiement:** _______________

**IP VPS:** _______________

**Domaine (optionnel):** _______________

**Déployé par:** _______________

**Statut:** [ ] En cours [ ] Complété [ ] Problèmes

**Notes:**
