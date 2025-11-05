# 📦 Guide d'Installation Rapide

Guide étape par étape pour installer et configurer le projet après l'avoir cloné depuis GitHub.

---

## ⚡ Installation Rapide (5 minutes)

### 1️⃣ Backend Python

```bash
# Aller dans le dossier backend
cd backend

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
venv\Scripts\activate

# Activer l'environnement (Linux/Mac)
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Créer le fichier .env
# Copiez le contenu ci-dessous dans un nouveau fichier .env
```

**Créer `backend/.env` :**
```env
DB_NAME=travel_app
DB_USER=root
DB_PASSWORD=votre_mot_de_passe
DB_HOST=127.0.0.1
DB_PORT=3306
```

**Configurer MySQL :**
```sql
CREATE DATABASE travel_app;
```

**Appliquer les migrations :**
```bash
python manage.py migrate
```

### 2️⃣ Frontend Node.js

```bash
# Aller dans le dossier frontend
cd frontend

# Installer les dépendances
npm install
```

### 3️⃣ Démarrer les serveurs

**Terminal 1 - Django :**
```bash
cd backend
venv\Scripts\activate  # Windows
python manage.py runserver 8001
```

**Terminal 2 - Llama :**
```bash
cd backend
venv\Scripts\activate  # Windows
python llama_server.py
```

**Terminal 3 - Frontend :**
```bash
cd frontend
npm run dev
```

---

## ✅ Vérification

1. Ouvrez http://localhost:5173 dans votre navigateur
2. Vérifiez http://127.0.0.1:8001/api/health/ (devrait retourner du JSON)
3. Vérifiez http://127.0.0.1:8000/health (devrait retourner `{"status": "OK"}`)

---

## ❌ Problèmes Courants

### "Module not found" après pip install

**Solution :** Vérifiez que vous avez activé l'environnement virtuel :
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Erreur de connexion MySQL

**Vérifiez :**
1. MySQL est démarré
2. Le fichier `.env` existe et contient les bons identifiants
3. La base de données `travel_app` existe

### Le port 8001 est déjà utilisé

**Windows :**
```bash
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

**Linux/Mac :**
```bash
lsof -i :8001
kill -9 <PID>
```

### "Cannot find module" dans le frontend

**Solution :**
```bash
cd frontend
rm -rf node_modules
npm install
```

---

## 📝 Notes Importantes

- ⚠️ **Ne commitez jamais** le fichier `.env` (il contient vos identifiants)
- ⚠️ **Ne commitez jamais** les dossiers `node_modules` et `venv` (déjà dans `.gitignore`)
- Le modèle Llama sera téléchargé automatiquement au premier démarrage (~2GB)

---

Pour plus de détails, consultez le [README.md](README.md) principal.

