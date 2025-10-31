# 🚀 Guide de démarrage des serveurs

## Architecture du projet

Le projet nécessite **2 serveurs** pour fonctionner correctement :

1. **Serveur Flask (Llama)** - Port **8000** : Gère l'IA conversationnelle
2. **Serveur Django** - Port **8001** : Gère l'API principale et le scraping

---

## 🎯 Démarrage rapide

### Option 1 : Scripts automatiques (Recommandé)

#### Windows :

1. **Terminal 1** - Serveur Llama :

   ```bash
   cd backend
   start_llama.bat
   ```

2. **Terminal 2** - Serveur Django :
   ```bash
   cd backend
   start_django.bat
   ```

---

### Option 2 : Commandes manuelles

#### Terminal 1 - Serveur Flask (Llama) :

```bash
cd backend
venv\Scripts\activate
python llama_server.py
```

✅ Devrait afficher : `Serveur Llama demarre sur http://0.0.0.0:8000`

#### Terminal 2 - Serveur Django :

```bash
cd backend
venv\Scripts\activate
python manage.py runserver 8001
```

✅ Devrait afficher : `Starting development server at http://127.0.0.1:8001/`

---

## ✅ Vérification

Une fois les deux serveurs démarrés, testez :

1. **Serveur Llama** : http://127.0.0.1:8000/health
   - Doit retourner : `{"status": "OK"}`

2. **Serveur Django** : http://127.0.0.1:8001/api/health/
   - Doit retourner un JSON avec les informations du serveur

3. **Frontend** : Assurez-vous que le frontend React est démarré sur le port 5173

---

## ❌ Dépannage

### "Le serveur Django ne répond pas"

**Causes possibles :**

1. Le serveur Django n'est pas démarré
   - Solution : Exécutez `start_django.bat` ou `python manage.py runserver 8001`

2. Le serveur tourne sur un autre port
   - Vérifiez les processus : `netstat -ano | findstr :8001`

3. Erreur de configuration
   - Exécutez : `python manage.py check`

### "Erreur CORS"

Si vous voyez des erreurs CORS dans la console :

- Vérifiez que `corsheaders` est dans `INSTALLED_APPS` dans `settings.py`
- Vérifiez que votre origine frontend (http://localhost:5173 ou http://127.0.0.1:5173) est dans `CORS_ALLOWED_ORIGINS`

### Le serveur Llama ne répond pas

1. Vérifiez que le modèle Llama est présent dans `venv/GPT4AllModels/`
2. Vérifiez que Flask démarre sans erreur
3. Testez : `curl http://127.0.0.1:8000/health`

---

## 📝 Notes importantes

- Les deux serveurs doivent tourner **en même temps**
- Ne fermez pas les fenêtres de terminal pendant l'utilisation
- Le frontend communique avec Django sur le port **8001**
- Django communique avec Llama sur le port **8000**

---

## 🔧 Commandes utiles

```bash
# Vérifier les ports utilisés
netstat -ano | findstr :8000
netstat -ano | findstr :8001

# Arrêter un processus sur un port (remplacez PID par le numéro du processus)
taskkill /PID <PID> /F

# Vérifier la configuration Django
python manage.py check

# Créer les migrations (si nécessaire)
python manage.py makemigrations
python manage.py migrate
```

---

## 🎉 Prêt !

Une fois les deux serveurs démarrés et vérifiés, vous pouvez utiliser le chatbot dans votre application frontend !
