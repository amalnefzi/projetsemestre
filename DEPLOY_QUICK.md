# ⚡ Déploiement Rapide - Version Simplifiée

Guide rapide pour déployer votre projet en 10 minutes.

## 🎯 Option 1 : Déploiement Local (Développement)

### Backend Django

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

pip install -r requirements.txt
cp .env.example .env
# Éditez .env avec vos paramètres

python manage.py migrate
python manage.py runserver 8001
```

### Serveur Llama

```bash
cd backend
# Dans un autre terminal, avec le venv activé
python llama_server.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

**✅ Tout fonctionne sur localhost !**

---

## 🌐 Option 2 : Déploiement Simple (VPS Ubuntu)

### Installation rapide

```bash
# 1. Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# 2. Installer Python, MySQL, Nginx
sudo apt install python3-pip python3-venv mysql-server nginx git -y

# 3. Cloner votre projet
cd /var/www
sudo git clone votre-repo.git travel-app
cd travel-app/backend

# 4. Créer venv et installer dépendances
sudo python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configurer .env
sudo cp .env.example .env
sudo nano .env  # Configurez vos valeurs

# 6. Configurer MySQL
sudo mysql -u root -p
# Dans MySQL :
CREATE DATABASE travel_app;
CREATE USER 'travel_user'@'localhost' IDENTIFIED BY 'votre_mdp';
GRANT ALL ON travel_app.* TO 'travel_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 7. Migrations
python manage.py migrate
python manage.py collectstatic --noinput

# 8. Installer Gunicorn
pip install gunicorn

# 9. Tester Gunicorn
gunicorn backend.wsgi:application --bind 0.0.0.0:8001
# Si ça marche, Ctrl+C et continuez
```

### Créer les services systemd

**Django** (`/etc/systemd/system/travel-django.service`) :

```ini
[Unit]
Description=Travel Django
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/travel-app/backend
Environment="PATH=/var/www/travel-app/backend/venv/bin"
ExecStart=/var/www/travel-app/backend/venv/bin/gunicorn backend.wsgi:application --bind unix:/tmp/travel-django.sock

[Install]
WantedBy=multi-user.target
```

**Llama** (`/etc/systemd/system/travel-llama.service`) :

```ini
[Unit]
Description=Travel Llama
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/travel-app/backend
Environment="PATH=/var/www/travel-app/backend/venv/bin"
ExecStart=/var/www/travel-app/backend/venv/bin/python llama_server.py

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable travel-django travel-llama
sudo systemctl start travel-django travel-llama
```

### Configuration Nginx simple

Créer `/etc/nginx/sites-available/travel` :

```nginx
server {
    listen 80;
    server_name votre-ip ou votre-domaine;

    # API Django
    location /api/ {
        proxy_pass http://unix:/tmp/travel-django.sock;
        proxy_set_header Host $host;
    }

    # Frontend (après build)
    location / {
        root /var/www/travel-app/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/travel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🚀 Option 3 : Déploiement Cloud (Railway/Render)

### Railway.app (Recommandé - Gratuit au début)

1. **Backend Django** :
   - Créez un nouveau projet sur Railway
   - Connectez votre repo GitHub
   - Point de départ : `backend/`
   - Build Command : `pip install -r requirements.txt && python manage.py migrate`
   - Start Command : `gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT`
   - Variables d'env : Ajoutez toutes vos variables `.env`

2. **Serveur Llama** :
   - Créez un autre service sur Railway
   - Même repo, même point de départ
   - Start Command : `python llama_server.py`
   - ⚠️ Nécessite plus de RAM (upgrade au plan payant)

3. **Frontend** :
   - Build sur Railway ou déployez sur Vercel/Netlify
   - Variable `VITE_API_URL` : URL de votre backend Railway

### Render.com

Similaire à Railway, créez 3 services séparés (Django, Llama, Frontend).

---

## 📝 Checklist Ultra-Rapide

- [ ] Backend : `.env` configuré
- [ ] Backend : Migrations appliquées
- [ ] Backend : `DEBUG=False` en prod
- [ ] Llama : Service démarré et accessible sur port 8000
- [ ] Frontend : `VITE_API_URL` pointant vers le bon backend
- [ ] Frontend : Build réussi (`npm run build`)
- [ ] Test : `/api/health/` répond
- [ ] Test : Chatbot fonctionne

---

## 🆘 Problèmes Courants

**Port déjà utilisé** :

```bash
sudo lsof -i :8001
sudo kill -9 <PID>
```

**Permissions** :

```bash
sudo chown -R www-data:www-data /var/www/travel-app
```

**Logs** :

```bash
sudo journalctl -u travel-django -f
sudo journalctl -u travel-llama -f
```

---

**Pour plus de détails, voir `DEPLOYMENT.md`** 📚
