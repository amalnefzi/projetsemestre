# 🚀 Guide de Déploiement - Projet Voyage

Ce guide vous explique comment déployer votre application de voyage complète (Backend Django + Flask Llama + Frontend React).

---

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Préparation](#préparation)
3. [Déploiement Backend Django](#déploiement-backend-django)
4. [Déploiement Serveur Llama (Flask)](#déploiement-serveur-llama-flask)
5. [Déploiement Frontend](#déploiement-frontend)
6. [Déploiement avec Docker (Optionnel)](#déploiement-avec-docker-optionnel)
7. [Configuration Production](#configuration-production)
8. [Services Recommandés](#services-recommandés)

---

## 🔧 Prérequis

### Système

- **Python** 3.10+ (recommandé 3.11 ou 3.12)
- **Node.js** 18+ et npm/yarn
- **MySQL** 8.0+ ou MariaDB 10.5+
- **Git**

### Pour le serveur Llama

- **4GB+ RAM** (recommandé 8GB pour le modèle)
- **Espace disque** : ~2GB pour le modèle Llama

---

## 📦 Préparation

### 1. Variables d'Environnement

Créez un fichier `.env` dans `backend/` :

```env
# Base de données MySQL
DB_NAME=travel_app
DB_USER=root
DB_PASSWORD=votre_mot_de_passe
DB_HOST=127.0.0.1
DB_PORT=3306

# Django
SECRET_KEY=votre_secret_key_django_genere_aleatoirement
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com

# CORS (URLs autorisées pour le frontend)
CORS_ALLOWED_ORIGINS=https://votre-domaine.com,https://www.votre-domaine.com
```

**⚠️ Important** :

- Générez une `SECRET_KEY` Django avec : `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- En production, **jamais** `DEBUG=True`

### 2. Mettre à jour les requirements.txt

Assurez-vous que `backend/requirements.txt` contient toutes les dépendances :

```txt
# Django et REST Framework
Django==5.2.6
djangorestframework==3.16.1
django-cors-headers==4.9.0
python-dotenv==1.1.1

# Base de données
mysqlclient==2.2.7

# Flask et Llama
Flask==3.0.0
flask-cors==4.0.0
gpt4all==2.5.0

# Utilitaires
requests==2.31.0
beautifulsoup4==4.12.0
lxml==4.9.3
```

---

## 🐍 Déploiement Backend Django

### Option A : Serveur VPS/Dedicated (Ubuntu/Debian)

#### 1. Installation des dépendances système

```bash
sudo apt update
sudo apt install python3-pip python3-venv mysql-server nginx git
sudo mysql_secure_installation
```

#### 2. Configuration MySQL

```bash
sudo mysql -u root -p
```

```sql
CREATE DATABASE travel_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'travel_user'@'localhost' IDENTIFIED BY 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON travel_app.* TO 'travel_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3. Déploiement de l'application

```bash
# Cloner ou uploader votre projet
cd /var/www
git clone votre-repo.git travel-app
cd travel-app/backend

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Configuration
cp .env.example .env
nano .env  # Éditer avec vos valeurs

# Migrations
python manage.py makemigrations
python manage.py migrate

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Créer un superutilisateur
python manage.py createsuperuser
```

#### 4. Configuration Gunicorn

Installer Gunicorn :

```bash
pip install gunicorn
```

Créer `/etc/systemd/system/travel-django.service` :

```ini
[Unit]
Description=Travel App Django Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/travel-app/backend
Environment="PATH=/var/www/travel-app/backend/venv/bin"
ExecStart=/var/www/travel-app/backend/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/travel-app/backend/backend.sock \
    backend.wsgi:application

[Install]
WantedBy=multi-user.target
```

Activer le service :

```bash
sudo systemctl daemon-reload
sudo systemctl start travel-django
sudo systemctl enable travel-django
```

#### 5. Configuration Nginx

Créer `/etc/nginx/sites-available/travel-app` :

```nginx
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    location / {
        proxy_pass http://unix:/var/www/travel-app/backend/backend.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/travel-app/backend/staticfiles/;
    }

    location /media/ {
        alias /var/www/travel-app/backend/media/;
    }
}
```

Activer le site :

```bash
sudo ln -s /etc/nginx/sites-available/travel-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Pour HTTPS (SSL)** :

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com
```

---

### Option B : Platform as a Service (PaaS)

#### Heroku

1. **Créer `Procfile`** dans `backend/` :

```
web: gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT
llama: python llama_server.py
```

2. **Heroku CLI** :

```bash
heroku create votre-app-name
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=votre_secret_key
git push heroku main
```

#### Railway / Render

- Railway : Connectez votre repo GitHub et configurez les variables d'environnement
- Render : Créez un Web Service et pointez vers `backend/`

---

## 🤖 Déploiement Serveur Llama (Flask)

### Option A : Même serveur que Django (Recommandé)

Créer `/etc/systemd/system/travel-llama.service` :

```ini
[Unit]
Description=Travel App Llama Flask Server
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/travel-app/backend
Environment="PATH=/var/www/travel-app/backend/venv/bin"
ExecStart=/var/www/travel-app/backend/venv/bin/python llama_server.py

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start travel-llama
sudo systemctl enable travel-llama
```

### Option B : Serveur séparé (Pour performances)

Déployez Flask Llama sur un serveur séparé avec plus de RAM/CPU pour l'IA.

---

## ⚛️ Déploiement Frontend

### 1. Build de production

```bash
cd frontend
npm install
npm run build
```

Cela crée un dossier `dist/` avec les fichiers statiques.

### Option A : Servir avec Nginx (Recommandé)

Ajouter à votre configuration Nginx :

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    # Frontend React
    root /var/www/travel-app/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API Backend
    location /api/ {
        proxy_pass http://unix:/var/www/travel-app/backend/backend.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option B : Vercel / Netlify

1. **Vercel** :

```bash
npm i -g vercel
cd frontend
vercel
```

Configurez `VITE_API_URL` dans les variables d'environnement Vercel.

2. **Netlify** :

- Connectez votre repo
- Build command : `cd frontend && npm run build`
- Publish directory : `frontend/dist`
- Variables d'environnement : `VITE_API_URL=https://api.votre-domaine.com`

---

## 🐳 Déploiement avec Docker (Optionnel)

### 1. Dockerfile Django

Créer `backend/Dockerfile` :

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Exposer le port
EXPOSE 8001

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8001"]
```

### 2. Dockerfile Flask Llama

Créer `backend/Dockerfile.llama` :

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir Flask flask-cors gpt4all requests

# Copier le modèle (si nécessaire)
COPY llama_server.py .
COPY venv/GPT4AllModels/ ./GPT4AllModels/

EXPOSE 8000

CMD ["python", "llama_server.py"]
```

### 3. docker-compose.yml

Créer `docker-compose.yml` à la racine :

```yaml
version: "3.8"

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: travel_app
      MYSQL_USER: travel_user
      MYSQL_PASSWORD: votre_mot_de_passe
      MYSQL_ROOT_PASSWORD: root_password
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

  django:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - DB_HOST=mysql
      - DB_NAME=travel_app
      - DB_USER=travel_user
      - DB_PASSWORD=votre_mot_de_passe
    depends_on:
      - mysql
    volumes:
      - ./backend:/app

  llama:
    build:
      context: ./backend
      dockerfile: Dockerfile.llama
    ports:
      - "8000:8000"
    volumes:
      - ./backend/venv/GPT4AllModels:/app/GPT4AllModels

volumes:
  mysql_data:
```

Démarrage :

```bash
docker-compose up -d
```

---

## 🔒 Configuration Production

### 1. Settings.py Production

Modifier `backend/backend/settings.py` :

```python
import os
from dotenv import load_dotenv
load_dotenv()

DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# CORS
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')

# Sécurité
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### 2. Sécurité

- ✅ **Ne jamais** commiter `.env` ou `SECRET_KEY`
- ✅ Utiliser HTTPS en production
- ✅ Configurer un firewall (UFW)
- ✅ Limiter les connexions MySQL à localhost
- ✅ Utiliser des mots de passe forts

---

## 🌐 Services Recommandés

### Hébergement Backend

- **VPS** : DigitalOcean, Linode, OVH (à partir de 5€/mois)
- **PaaS** : Railway, Render, Fly.io
- **Cloud** : AWS EC2, Google Cloud Compute, Azure

### Hébergement Frontend

- **Vercel** : Gratuit, excellent pour React
- **Netlify** : Gratuit, similaire à Vercel
- **Cloudflare Pages** : Gratuit et rapide

### Base de données

- **MySQL** : Sur le même serveur (développement)
- **Managed DB** : AWS RDS, Google Cloud SQL, PlanetScale (production)

---

## 📝 Checklist de Déploiement

- [ ] Variables d'environnement configurées
- [ ] Base de données créée et migrations appliquées
- [ ] `DEBUG=False` en production
- [ ] `SECRET_KEY` générée et sécurisée
- [ ] Fichiers statiques collectés
- [ ] HTTPS configuré (SSL/TLS)
- [ ] CORS configuré correctement
- [ ] Services systemd configurés et actifs
- [ ] Nginx configuré et testé
- [ ] Frontend buildé et déployé
- [ ] Tests de connexion Django ↔ Llama
- [ ] Monitoring/logs configurés

---

## 🆘 Dépannage

### Django ne démarre pas

```bash
sudo systemctl status travel-django
sudo journalctl -u travel-django -n 50
```

### Llama ne répond pas

```bash
curl http://localhost:8000/health
sudo systemctl status travel-llama
```

### Erreurs CORS

Vérifiez que `CORS_ALLOWED_ORIGINS` contient l'URL exacte du frontend.

### Erreurs MySQL

```bash
sudo mysql -u root -p
SHOW DATABASES;
```

---

## 📞 Support

Pour toute question, consultez :

- [Documentation Django](https://docs.djangoproject.com/)
- [Documentation Flask](https://flask.palletsprojects.com/)
- [Documentation Vite](https://vitejs.dev/)

---

**Bon déploiement ! 🚀**
