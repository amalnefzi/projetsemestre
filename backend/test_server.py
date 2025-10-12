"""
Script pour tester la connexion complète Flask → Django → Scraping
"""

import requests
import json

print("🧪 Test de la configuration complète\n")
print("="*60)

# Test 1: Flask (Llama) sur port 8000
print("\n1️⃣ Test Flask (Llama) sur port 8000...")
try:
    response = requests.get("http://127.0.0.1:8000/health", timeout=3)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Flask OK - Modèle chargé: {data.get('model_loaded')}")
    else:
        print(f"❌ Flask erreur: {response.status_code}")
except Exception as e:
    print(f"❌ Flask inaccessible: {e}")
    print("💡 Lance: python llama_server.py")

# Test 2: Django sur port 8001
print("\n2️⃣ Test Django sur port 8001...")
try:
    response = requests.get("http://127.0.0.1:8001/api/health/", timeout=3)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Django OK")
        print(f"   Status: {data.get('status')}")
        llama_info = data.get('llama', {})
        print(f"   Llama connecté: {llama_info.get('status')}")
    else:
        print(f"❌ Django erreur: {response.status_code}")
except Exception as e:
    print(f"❌ Django inaccessible: {e}")
    print("💡 Lance: python manage.py runserver 8001")

# Test 3: Chat complet via Django
print("\n3️⃣ Test du chat complet (Django → Llama → Scraping)...")
try:
    message = "Je cherche un hôtel pas cher à Tunis"
    print(f"   Message: '{message}'")
    
    response = requests.post(
        "http://127.0.0.1:8001/api/intelligent_travel_chat/",
        json={"message": message, "user_id": 1},
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Chat OK")
        print(f"\n   🤖 Réponse IA: {data.get('ai_response', 'N/A')[:100]}...")
        
        annonces = data.get('annonces', [])
        print(f"\n   📊 Annonces trouvées: {len(annonces)}")
        for i, annonce in enumerate(annonces[:3], 1):
            print(f"      {i}. {annonce.get('nom')} - {annonce.get('prix')} DT (⭐ {annonce.get('note')})")
        
        prefs = data.get('detected_preferences', {})
        print(f"\n   🎯 Préférences détectées:")
        print(f"      Budget: {prefs.get('budget')}")
        print(f"      Destination: {prefs.get('destination')}")
        print(f"      Intérêts: {prefs.get('interests')}")
        
    else:
        print(f"❌ Chat erreur: {response.status_code}")
        print(f"   Réponse: {response.text[:200]}")
except Exception as e:
    print(f"❌ Chat inaccessible: {e}")

# Test 4: MySQL
print("\n4️⃣ Test connexion MySQL...")
try:
    import MySQLdb
    try:
        conn = MySQLdb.connect(
            host='localhost',
            user='root',
            password='',
            database='travel_app'
        )
        print("✅ MySQL OK - Base 'travel_app' accessible")
        conn.close()
    except MySQLdb.OperationalError as e:
        if '1049' in str(e):
            print("⚠️ MySQL OK mais base 'travel_app' n'existe pas")
            print("💡 Crée la base dans phpMyAdmin ou lance:")
            print("   mysql -u root -e 'CREATE DATABASE travel_app;'")
        else:
            print(f"❌ MySQL erreur: {e}")
except ImportError:
    print("⚠️ MySQLdb non installé (pas grave si tu utilises SQLite)")

print("\n" + "="*60)
print("\n📋 RÉSUMÉ:")
print("✅ = OK | ❌ = Problème | ⚠️ = Attention\n")

# Recommandations
print("💡 PROCHAINES ÉTAPES:")
print("1. Assure-toi que Flask (port 8000) ET Django (port 8001) tournent")
print("2. Dans React, utilise: http://127.0.0.1:8001")
print("3. Utilise l'endpoint: /api/intelligent_travel_chat/")
print("\n🚀 Commandes pour démarrer:")
print("   Terminal 1: python llama_server.py")
print("   Terminal 2: python manage.py runserver 8001")
print("   Terminal 3: cd frontend && npm run dev")