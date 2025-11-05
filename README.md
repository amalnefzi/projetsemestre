# 🗺️ Projet Semestre - Application de Voyage

Application web de recommandation de voyages avec IA conversationnelle.

## 🏗️ Architecture

Le projet est composé de 3 parties principales :

1. **Backend Django** (Port 8001) - API principale et scraping
2. **Serveur Llama/Flask** (Port 8000) - IA conversationnelle
3. **Frontend React/TypeScript** (Port 5173) - Interface utilisateur

---

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Python** 3.10+ (recommandé 3.11 ou 3.12)
- **Node.js** 18+ et npm
- **MySQL** 8.0+ (ou MariaDB 10.5+)
- **Git**

---

## 🚀 Installation et Configuration

### Étape 1 : Cloner le projet

```bash
git clone <votre-repo-url>
cd projetsemestre
```

### Étape 2 : Configuration du Backend

#### 2.1 Créer l'environnement virtuel Python

```bash
cd backend
python -m venv venv
```

**Windows :**
```bash
venv\Scripts\activate
```

**Linux/Mac :**
```bash
source venv/bin/activate
```

#### 2.2 Installer les dépendances Python

```bash
pip install -r requirements.txt
```

#### 2.3 Configurer la base de données MySQL

Créez une base de données MySQL :

```sql
CREATE DATABASE travel_app;
CREATE USER 'travel_user'@'localhost' IDENTIFIED BY 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON travel_app.* TO 'travel_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 2.4 Créer le fichier .env

Créez un fichier `.env` dans le dossier `backend/` :

```env
# Base de données MySQL
DB_NAME=travel_app
DB_USER=travel_user
DB_PASSWORD=votre_mot_de_passe
DB_HOST=127.0.0.1
DB_PORT=3306

# Django (optionnel en développement)
# SECRET_KEY=votre_secret_key
# DEBUG=True
```

**⚠️ Note :** Pour générer une SECRET_KEY Django :
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 2.5 Appliquer les migrations

```bash
python manage.py migrate
```

### Étape 3 : Configuration du Frontend

```bash
cd ../frontend
npm install
```

---

## ▶️ Démarrage du Projet

### Option 1 : Scripts automatiques (Windows)

**Terminal 1 - Serveur Llama :**
```bash
cd backend
start_llama.bat
```

**Terminal 2 - Serveur Django :**
```bash
cd backend
start_django.bat
```

**Terminal 3 - Frontend :**
```bash
cd frontend
npm run dev
```

### Option 2 : Commandes manuelles

**Terminal 1 - Serveur Llama (Flask) :**
```bash
cd backend
venv\Scripts\activate  # Windows
# ou: source venv/bin/activate  # Linux/Mac
python llama_server.py
```

**Terminal 2 - Serveur Django :**
```bash
cd backend
venv\Scripts\activate  # Windows
# ou: source venv/bin/activate  # Linux/Mac
python manage.py runserver 8001
```

**Terminal 3 - Frontend :**
```bash
cd frontend
npm run dev
```

---

## ✅ Vérification

Une fois tous les serveurs démarrés, vérifiez que tout fonctionne :

1. **Serveur Llama** : http://127.0.0.1:8000/health
   - Devrait retourner : `{"status": "OK"}`

2. **Serveur Django** : http://127.0.0.1:8001/api/health/
   - Devrait retourner un JSON avec les informations du serveur

3. **Frontend** : http://localhost:5173
   - L'interface devrait s'afficher

---

## ❌ Dépannage

### Le serveur Django ne démarre pas

**Erreur de connexion à la base de données :**
- Vérifiez que MySQL est démarré
- Vérifiez les identifiants dans `.env`
- Vérifiez que la base de données existe : `mysql -u root -p` puis `SHOW DATABASES;`

**Erreur de port déjà utilisé :**
```bash
# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8001
kill -9 <PID>
```

### Le serveur Llama ne démarre pas

- Vérifiez que le modèle Llama est présent dans `backend/venv/GPT4AllModels/`
- Le modèle sera téléchargé automatiquement au premier démarrage (peut prendre du temps)

### Erreurs CORS

Si vous voyez des erreurs CORS dans la console du navigateur :
- Vérifiez que `corsheaders` est dans `INSTALLED_APPS` dans `backend/backend/settings.py`
- Vérifiez que `http://localhost:5173` est dans `CORS_ALLOWED_ORIGINS`

### Le frontend ne se connecte pas au backend

- Vérifiez que le backend Django tourne sur le port 8001
- Vérifiez les URLs dans le code frontend (devraient pointer vers `http://localhost:8001`)

---

## 📁 Structure du Projet

```
projetsemestre/
├── backend/              # Backend Django et Flask
│   ├── api/              # Application Django API
│   ├── backend/          # Configuration Django
│   ├── llama_server.py   # Serveur Flask pour l'IA
│   ├── requirements.txt  # Dépendances Python
│   ├── manage.py         # Script de gestion Django
│   └── .env              # Variables d'environnement (à créer)
├── frontend/             # Frontend React/TypeScript
│   ├── src/              # Code source
│   ├── package.json      # Dépendances Node.js
│   └── vite.config.ts    # Configuration Vite
└── README.md             # Ce fichier
```

---

## 📚 Documentation Additionnelle

- **Guide de démarrage détaillé** : `backend/README_DEMARRAGE.md`
- **Guide de déploiement rapide** : `DEPLOY_QUICK.md`
- **Guide de déploiement complet** : `DEPLOYMENT.md`

---

## 🛠️ Commandes Utiles

### Backend

```bash
# Créer des migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur Django
python manage.py createsuperuser

# Vérifier la configuration
python manage.py check
```

### Frontend

```bash
# Démarrer le serveur de développement
npm run dev

# Build pour la production
npm run build

# Prévisualiser le build
npm run preview
```

---

## 👥 Pour les Nouveaux Développeurs

Si vous venez de cloner le projet :

1. ✅ Suivez les étapes d'installation ci-dessus
2. ✅ Créez votre fichier `.env` dans `backend/`
3. ✅ Configurez MySQL avec vos identifiants
4. ✅ Installez les dépendances (Python et Node.js)
5. ✅ Démarrez les serveurs dans l'ordre

**⚠️ Important :** 
- Ne commitez **jamais** le fichier `.env` (il contient des informations sensibles)
- Ne commitez **jamais** les dossiers `node_modules` et `venv` (ils sont dans `.gitignore`)

---

## 📝 Notes

- Les deux serveurs backend (Django et Llama) doivent tourner **en même temps**
- Le frontend communique avec Django sur le port **8001**
- Django communique avec Llama sur le port **8000**
- Le modèle Llama nécessite ~2GB d'espace disque

---

## 🎉 Prêt !

Une fois tous les serveurs démarrés, vous pouvez utiliser l'application dans votre navigateur à l'adresse http://localhost:5173
