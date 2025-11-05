from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import serializers, status
from django.db import connection
from .models import Destination, UserPreference
from urllib.parse import quote_plus

# -----------------------------
# CONFIGURATION DE LLAMA
# -----------------------------
LLAMA_URL = "http://127.0.0.1:8000/api/chat/"  # ✅ CORRIGÉ : Flask sur 8000, pas 8001
HEALTH_URL = "http://127.0.0.1:8000/health"

# -----------------------------
# MODE GRATUIT (Sans APIs payantes ni scraping agressif)
# -----------------------------
# Quand activé, on évite toute requête HTTP de scraping et on renvoie uniquement
# des deep links publics (Booking/Expedia/Airbnb/TripAdvisor/Google Flights).
FREE_MODE = True

# Verrou pour éviter les détections multiples simultanées
import threading
_detection_lock = threading.Lock()
_last_detection_time = 0
_detection_cooldown = 5  # Secondes entre deux détections

def detect_llama_url(force=False):
    """
    Détecte l'URL du serveur Llama avec verrou pour éviter les appels multiples.
    
    Args:
        force: Si True, ignore le cooldown et force la détection
    """
    global _last_detection_time, LLAMA_DETECTED
    
    # Vérifier le cooldown pour éviter trop de tentatives (sauf si force=True)
    import time
    current_time = time.time()
    if not force and current_time - _last_detection_time < _detection_cooldown:
        # Trop tôt depuis la dernière détection, retourner la valeur actuelle
        return LLAMA_DETECTED
    
    with _detection_lock:
        # Vérifier à nouveau après avoir acquis le verrou
        if not force and current_time - _last_detection_time < _detection_cooldown:
            return LLAMA_DETECTED
        
        _last_detection_time = current_time
        
        possible_health_urls = [
            "http://127.0.0.1:8000/health",  # Flask Llama
            "http://localhost:8000/health",
        ]
        
        for url in possible_health_urls:
            try:
                print(f"🔍 Test de connexion à: {url}")
                # ✅ Timeout augmenté à 5 secondes pour le chargement du modèle
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ Serveur Llama détecté à {url}")
                    # Retourner l'URL du chat, pas celle du health
                    base_url = url.replace('/health', '')
                    return f"{base_url}/api/chat/"
            except requests.exceptions.Timeout:
                print(f"⏱️ Timeout connexion à {url} (serveur peut être en cours de chargement)")
                continue
            except Exception as e:
                print(f"⚠️ Erreur connexion à {url}: {type(e).__name__}")
                continue
        
        print("❌ Aucune URL Llama détectée - Mode simulation activé")
        return None

# Variable globale pour stocker l'URL détectée
LLAMA_DETECTED = detect_llama_url()

# -----------------------------
# ✅ FONCTION HEALTH (AMÉLIORÉE - Détection dynamique)
# -----------------------------
@api_view(["GET"])
def health(request):
    """
    Endpoint de vérification de santé du serveur Django
    """
    global LLAMA_DETECTED
    llama_status = "disconnected"
    llama_url = None
    
    # ✅ Réessayer de détecter Llama si pas encore détecté (détection dynamique)
    # Mais seulement si le cooldown est respecté pour éviter les boucles
    if not LLAMA_DETECTED:
        print("🔄 Réessai de détection Llama...")
        LLAMA_DETECTED = detect_llama_url()
    
    # Tester la connexion à Llama
    if LLAMA_DETECTED:
        try:
            # ✅ Timeout augmenté pour permettre au serveur de répondre
            health_check = requests.get(HEALTH_URL, timeout=5)
            if health_check.status_code == 200:
                llama_status = "connected"
                llama_url = LLAMA_DETECTED
            else:
                llama_status = "error"
                print(f"⚠️ Llama répond avec code {health_check.status_code}")
        except requests.exceptions.Timeout:
            llama_status = "timeout"
            print(f"⏱️ Timeout lors de la vérification de Llama (peut être en cours de chargement)")
        except Exception as e:
            llama_status = "error"
            print(f"⚠️ Erreur connexion Llama: {type(e).__name__}")
    else:
        # Réessayer une dernière fois (avec cooldown)
        LLAMA_DETECTED = detect_llama_url()
        if LLAMA_DETECTED:
            try:
                health_check = requests.get(HEALTH_URL, timeout=5)
                if health_check.status_code == 200:
                    llama_status = "connected"
                    llama_url = LLAMA_DETECTED
            except:
                llama_status = "error"
    
    return Response({
        "status": "healthy",
        "service": "Django Backend",
        "timestamp": datetime.now().isoformat(),
        "llama": {
            "status": llama_status,
            "url": llama_url
        },
        "endpoints": {
            "chat": "/api/chat/",
            "intelligent_travel_chat": "/api/intelligent_travel_chat/",
            "destinations": "/api/destinations/",
            "recommendations": "/api/recommendations/"
        }
    })

# -----------------------------
# APPEL AU SERVEUR LLAMA
# -----------------------------
def call_llama_api(prompt, max_tokens=150):
    """
    Appel au serveur Llama Flask. Retourne la réponse texte.
    """
    global LLAMA_DETECTED
    
    # ✅ Réessayer de détecter Llama si pas encore détecté
    if not LLAMA_DETECTED:
        print("🔄 Réessai de détection Llama avant appel API...")
        LLAMA_DETECTED = detect_llama_url()
    
    if not LLAMA_DETECTED:
        return f"[Simulation] Réponse pour: {prompt[:50]}..."

    try:
        payload = {
            "message": prompt,
            "user_id": 1
        }
        print(f"📤 Envoi à Llama: {LLAMA_DETECTED}")
        response = requests.post(LLAMA_DETECTED, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            if "ai_response" in data:
                return data["ai_response"]
            elif "response" in data:
                return data["response"]
            return str(data)[:200]
        else:
            # En production on ne casse pas l'expérience utilisateur : on fallback
            print(f"❌ Erreur API Llama: {response.status_code} -> fallback simulation")
            # Réessayer la détection en cas d'erreur (non bloquant)
            LLAMA_DETECTED = detect_llama_url()
            return f"[Simulation] Réponse pour: {prompt[:50]}..."
    except Exception as e:
        # Ne pas exposer l'erreur brute au frontend; fallback
        print(f"❌ Erreur connexion Llama: {str(e)} -> fallback simulation")
        # Réessayer la détection en cas d'exception (non bloquant)
        LLAMA_DETECTED = detect_llama_url()
        return f"[Simulation] Réponse pour: {prompt[:50]}..."

# -----------------------------
# VUE CHAT SIMPLE
# -----------------------------
@api_view(['POST'])
def chat_view(request):
    """
    Reçoit le message de l'utilisateur, envoie à Llama et retourne la réponse.
    """
    try:
        data = json.loads(request.body)
        message = data.get("message", "")
        print(f"📨 Message reçu: {message}")

        # Appel Llama
        llama_response = call_llama_api(message)
        print(f"🤖 Réponse Llama: {llama_response}")

        return JsonResponse({
            "response": llama_response,
            "status": "success",
            "llama_used": bool(LLAMA_DETECTED)
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# -----------------------------
# ANALYSE INTELLIGENTE DU VOYAGE
# -----------------------------
def analyze_travel_intent_with_llama(user_message):
    """
    Utilise Llama pour analyser l'intention de voyage.
    """
    prompt = (
        "Tu es un assistant d'analyse d'intention de voyage. "
        "Ton rôle est d'extraire les préférences STRICTEMENT au format JSON. "
        "Ne dis RIEN d'autre que l'objet JSON unique, sans texte autour.\n\n"
        f"Message: \"{user_message}\"\n\n"
        "Format JSON requis:\n"
        "{\n"
        "  \"destination\": \"ville principale\" | null,\n"
        "  \"budget\": nombre | null,\n"
        "  \"type_hebergement\": \"hôtel/appartement/maison\" | null,\n"
        "  \"duree\": nombre | null,\n"
        "  \"personnes\": nombre | null,\n"
        "  \"interets\": [\"plage\", \"culture\", \"nature\", \"ville\"] | []\n"
        "}\n\n"
        "Réponse JSON:"
    )

    response = call_llama_api(prompt)
    try:
        # Éviter de parser l'exemple si la réponse contient le prompt (mode simulation)
        if response.startswith("[Simulation]"):
            raise ValueError("Simulation -> fallback")

        # Rechercher tous les objets JSON et préférer le dernier valide
        candidates = re.findall(r'\{[\s\S]*?\}', response)
        for raw in reversed(candidates):
            try:
                obj = json.loads(raw)
                if isinstance(obj, dict) and "destination" in obj:
                    print(f"🎯 Intention Llama: {obj}")
                    return obj
            except Exception:
                continue

        # Si la réponse entière est un JSON valide
        obj = json.loads(response)
        if isinstance(obj, dict):
            print(f"🎯 Intention Llama direct: {obj}")
            return obj
    except Exception as e:
        print(f"❌ Erreur parsing JSON Llama: {e}")

    return extract_intent_manual(user_message)

def extract_intent_manual(message):
    """
    Fallback manuel si Llama échoue.
    """
    # 💡 L'erreur précédente 'message_lower' non défini se produit si cette ligne
    # n'est pas la première instruction. Elle est correctement placée ici.
    message_lower = message.lower()
    
    intent = {
        "destination": None, # Pas de contrainte locale: aucune destination par défaut
        "budget": 100,          # Budget par défaut (en DT, pour le scraping)
        "type_hebergement": "hôtel",
        "duree": 3,
        "personnes": 2,
        "interets": []
    }

    # Détection destination (globale)
    # 1) Regex basée sur prépositions courantes (à, vers, pour, to) en conservant la casse
    try:
        prepo_regex = re.compile(r"(?:\bà\b|\bvers\b|\bpour\b|\bto\b)\s+([A-ZÀÂÄÉÈÊËÎÏÔÖÛÜŸ][\w'’\-éèàùâäêëîïôöûüç]+(?:\s+[A-ZÀÂÄÉÈÊËÎÏÔÖÛÜŸ][\w'’\-éèàùâäêëîïôöûüç]+){0,3})")
        m = prepo_regex.search(message)
        if m:
            candidate = m.group(1).strip()
            # éviter de capter des mots trop génériques
            if len(candidate) >= 3:
                intent["destination"] = candidate
    except Exception:
        pass

    # 2) Liste de villes connues rapides (fallback léger) sur message_lower
    if 'paris' in message_lower:
        intent["destination"] = "Paris"
    elif 'marrakech' in message_lower or 'maroc' in message_lower:
        intent["destination"] = "Marrakech"
    elif 'barcelone' in message_lower:
        intent["destination"] = "Barcelone"
    elif 'rome' in message_lower:
        intent["destination"] = "Rome"
    elif 'dubai' in message_lower:
        intent["destination"] = "Dubaï"
    # Tunisie (toujours supportée mais non imposée)
    elif 'hammamet' in message_lower or 'hamamet' in message_lower:
        intent["destination"] = "Hammamet"
    elif 'sousse' in message_lower:
        intent["destination"] = "Sousse"
    elif 'djerba' in message_lower:
        intent["destination"] = "Djerba"
    # 🌍 Pays/villes fréquents en minuscules (détection globale simple)
    elif 'canada' in message_lower:
        intent["destination"] = "Canada"
    elif 'new york' in message_lower:
        intent["destination"] = "New York"
    elif 'london' in message_lower or 'londres' in message_lower:
        intent["destination"] = "Londres"
    elif 'tokyo' in message_lower:
        intent["destination"] = "Tokyo"
    elif 'madrid' in message_lower:
        intent["destination"] = "Madrid"
    elif 'berlin' in message_lower:
        intent["destination"] = "Berlin"
    elif 'istanbul' in message_lower:
        intent["destination"] = "Istanbul"
    elif 'barcelona' in message_lower:
        intent["destination"] = "Barcelone"
    elif 'montreal' in message_lower or 'montréal' in message_lower:
        intent["destination"] = "Montréal"
    elif 'quebec' in message_lower or 'québec' in message_lower:
        intent["destination"] = "Québec"
    elif 'toronto' in message_lower:
        intent["destination"] = "Toronto"
    elif 'vancouver' in message_lower:
        intent["destination"] = "Vancouver"

    # 3) Fallback ultra simple: si rien détecté mais le message contient un mot capitalisé non initial
    if not intent["destination"]:
        try:
            tokens = re.findall(r"\b[A-ZÀÂÄÉÈÊËÎÏÔÖÛÜŸ][a-zàâäéèêëîïôöûüç'’\-]+\b", message)
            if tokens:
                # Prendre le dernier token capitalisé (souvent la ville en fin de phrase)
                intent["destination"] = tokens[-1]
        except Exception:
            pass

    # Détection budget
    budget_match = re.search(r'(\d+)\s*(dt|dinars|euros?|€)', message_lower)
    if budget_match:
        intent["budget"] = int(budget_match.group(1))
        # Conversion Euro -> Dinars (approximation 1 EUR ≈ 3 TND)
        if 'euro' in message_lower or '€' in message_lower:
            intent["budget"] = intent["budget"] * 3

    # Détection durée (nuits/jours)
    try:
        duree_match = re.search(r'(\d+)\s*(nuits?|jours?)', message_lower)
        if duree_match:
            intent["duree"] = int(duree_match.group(1))
    except Exception:
        pass

    # Détection personnes
    try:
        pers_match = re.search(r'pour\s+(\d+)\s*(personnes?|pers|pax?)', message_lower)
        if pers_match:
            intent["personnes"] = int(pers_match.group(1))
    except Exception:
        pass
    
    # Détection intérêts (utilisation de "not in" pour éviter les doublons)
    if 'plage' in message_lower or 'mer' in message_lower:
        if "plage" not in intent["interets"]:
            intent["interets"].append("plage")
            
    if 'culture' in message_lower or 'musée' in message_lower:
        if "culture" not in intent["interets"]:
            intent["interets"].append("culture")
            
    if 'nature' in message_lower or 'montagne' in message_lower:
        if "nature" not in intent["interets"]:
            intent["interets"].append("nature")
    
    return intent
# -----------------------------
# SCRAPING
# -----------------------------
def scrape_real_travel_offers(destination, budget, personnes=2):
    annonces = []
    print(f"🌐 Début préparation des offres pour {destination} (FREE_MODE={FREE_MODE})...")

    # En mode gratuit: ne faire que des deep links (pas de scraping HTTP)
    if FREE_MODE:
        # Estimation très simple: budget (par nuit) * durée
        estimated = None
        try:
            estimated = max(1, int(budget))
            # La durée sera ajoutée côté appelant; ici on garde estimation par nuit
        except Exception:
            estimated = None
        # prix_total_estime = prix_par_nuit * duree
        estimated_total = None
        try:
            estimated_total = int(estimated) * 1  # durée inconnue ici (géré plus haut)
        except Exception:
            estimated_total = None
        deep_links = build_deep_links(destination, adultes=personnes, estimated_price=estimated, estimated_total=estimated_total)
        annonces.extend(deep_links)
        if not annonces:
            annonces = generate_fallback_offers(destination, budget)
        return annonces[:10]

    # Mode normal (si jamais vous désactivez FREE_MODE): tenter des scrapes légers + deep links
    try:
        ta_offers = scrape_tripadvisor(destination, budget)
        annonces.extend(ta_offers)
        print(f"✅ TripAdvisor: {len(ta_offers)} offres")
    except Exception as e:
        print(f"❌ Erreur TripAdvisor: {e}")

    try:
        booking_offers = scrape_booking_simulation(destination, budget)
        annonces.extend(booking_offers)
        print(f"✅ Booking.com: {len(booking_offers)} offres")
    except Exception as e:
        print(f"❌ Erreur Booking.com: {e}")

    try:
        expedia_offers = scrape_expedia_simulation(destination, budget)
        annonces.extend(expedia_offers)
        print(f"✅ Expedia: {len(expedia_offers)} offres")
    except Exception as e:
        print(f"❌ Erreur Expedia: {e}")

    try:
        deep_links = build_deep_links(
            destination,
            adultes=personnes,
            estimated_price=budget,
            estimated_total=(budget * 1)
        )
        annonces.extend(deep_links)
        print(f"🔗 Deep links ajoutés: {len(deep_links)}")
    except Exception as e:
        print(f"⚠️ Erreur deep links: {e}")

    if not annonces:
        annonces = generate_fallback_offers(destination, budget)
    return annonces[:10]

def scrape_tripadvisor(destination, budget):
    try:
        import random
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        q = quote_plus(f"{destination} hotels")
        search_url = f"https://www.tripadvisor.com/Search?q={q}"
        response = requests.get(search_url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        offers = []
        cards = soup.find_all('div', class_=re.compile(r'result|listing|card|property'))
        
        for card in cards[:8]:
            name_elem = card.find(['h3', 'h2', 'span'])
            name = name_elem.get_text(strip=True) if name_elem else f"Hôtel {destination}"
            price = random.randint(int(budget*0.6), int(budget*1.2))
            rating = round(random.uniform(3.5, 4.9), 1)
            offers.append({
                "nom": name,
                "prix": price,
                "note": rating,
                "lien": search_url,
                "source": "TripAdvisor"
            })
        return offers
    except:
        return []

def scrape_booking_simulation(destination, budget):
    import random
    hotels = [
        f"Hôtel {destination} Central",
        f"Résidence {destination} Premium",
        f"Appartement {destination} Vue Mer",
        f"Suites {destination} Business",
        f"Villa {destination} Jardin"
    ]
    offers = []
    for hotel in hotels:
        price = random.randint(int(budget*0.5), int(budget*1.3))
        rating = round(random.uniform(3.8, 4.9), 1)
        if price <= budget * 1.2:
            q = quote_plus(destination)
            offers.append({
                "nom": hotel,
                "prix": price,
                "note": rating,
                "lien": f"https://www.booking.com/searchresults.html?ss={q}",
                "source": "Booking.com"
            })
    return offers

def scrape_expedia_simulation(destination, budget):
    import random
    types = ["Hôtel", "Resort", "Guesthouse", "Hostel", "Lodge"]
    offers = []
    for i in range(4):
        type_heb = random.choice(types)
        price = random.randint(int(budget*0.4), int(budget*1.4))
        rating = round(random.uniform(3.6, 4.8), 1)
        offers.append({
            "nom": f"{type_heb} {destination}",
            "prix": price,
            "note": rating,
            "lien": f"https://www.expedia.fr/Hotel-Search?destination={quote_plus(destination)}",
            "source": "Expedia"
        })
    return offers

def build_deep_links(destination, checkin=None, checkout=None, adultes=2, estimated_price=None, estimated_total=None):
    """
    Génère des liens directs (deep links) vers des pages de réservation réelles
    pour la destination demandée. Aucun scraping ni clé API requis.
    """
    q = quote_plus(destination) if destination else None

    links = []

    # Booking.com (hôtels)
    booking_url = f"https://www.booking.com/searchresults.html?ss={q}" if q else "https://www.booking.com/"
    if checkin and checkout:
        booking_url += f"&checkin={checkin}&checkout={checkout}&group_adults={adultes}"
    links.append({
        "nom": f"Hôtels à {destination} (Booking)" if destination else "Hôtels (Booking)",
        "prix": int(estimated_price) if isinstance(estimated_price, (int, float)) else None,
        "prix_par_nuit": int(estimated_price) if isinstance(estimated_price, (int, float)) else None,
        "prix_total_estime": int(estimated_total) if isinstance(estimated_total, (int, float)) else None,
        "note": None,
        "lien": booking_url,
        "source": "Booking.com"
    })

    # Expedia (hôtels)
    expedia_url = f"https://www.expedia.fr/Hotel-Search?destination={q}" if q else "https://www.expedia.fr/"
    links.append({
        "nom": f"Hôtels à {destination} (Expedia)" if destination else "Hôtels (Expedia)",
        "prix": int(estimated_price) if isinstance(estimated_price, (int, float)) else None,
        "prix_par_nuit": int(estimated_price) if isinstance(estimated_price, (int, float)) else None,
        "prix_total_estime": int(estimated_total) if isinstance(estimated_total, (int, float)) else None,
        "note": None,
        "lien": expedia_url,
        "source": "Expedia"
    })

    # Airbnb (logements)
    airbnb_url = f"https://www.airbnb.com/s/{q}/homes" if q else "https://www.airbnb.com/"
    links.append({
        "nom": f"Logements à {destination} (Airbnb)" if destination else "Logements (Airbnb)",
        "prix": int(estimated_price) if isinstance(estimated_price, (int, float)) else None,
        "prix_par_nuit": int(estimated_price) if isinstance(estimated_price, (int, float)) else None,
        "prix_total_estime": int(estimated_total) if isinstance(estimated_total, (int, float)) else None,
        "note": None,
        "lien": airbnb_url,
        "source": "Airbnb"
    })

    # TripAdvisor (hôtels)
    trip_url = (
        f"https://www.tripadvisor.com/Search?q={quote_plus(destination + ' hotels')}"
        if destination else "https://www.tripadvisor.com/"
    )
    links.append({
        "nom": f"Hôtels à {destination} (TripAdvisor)" if destination else "Hôtels (TripAdvisor)",
        "prix": int(estimated_price) if isinstance(estimated_price, (int, float)) else None,
        "prix_par_nuit": int(estimated_price) if isinstance(estimated_price, (int, float)) else None,
        "prix_total_estime": int(estimated_total) if isinstance(estimated_total, (int, float)) else None,
        "note": None,
        "lien": trip_url,
        "source": "TripAdvisor"
    })

    # Google Flights (vols) — lien de recherche public
    flights_url = f"https://www.google.com/travel/flights?q={q}" if q else "https://www.google.com/travel/flights"
    links.append({
        "nom": f"Vols vers {destination} (Google Flights)" if destination else "Vols (Google Flights)",
        "prix": None,
        "note": None,
        "lien": flights_url,
        "source": "Google"
    })

    return links

def generate_fallback_offers(destination, budget):
    return [
        {
            "nom": f"Hôtel {destination} Centre",
            "prix": int(budget*0.8),
            "note": 4.2,
            "lien": "https://example.com",
            "source": "Fallback"
        },
        {
            "nom": f"Résidence {destination}",
            "prix": int(budget*1.1),
            "note": 4.5,
            "lien": "https://example.com",
            "source": "Fallback"
        },
        {
            "nom": f"Auberge {destination}",
            "prix": int(budget*0.5),
            "note": 3.9,
            "lien": "https://example.com",
            "source": "Fallback"
        }
    ]

# -----------------------------
# ENDPOINT PRINCIPAL
# -----------------------------
@api_view(["POST"])
def intelligent_travel_chat(request):
    """
    ENDPOINT PRINCIPAL - Llama API + Scraping réel
    """
    try:
        user_message = request.data.get('message', '').strip()
        if not user_message:
            return Response({"error": "Message vide"}, status=400)

        print(f"📨 Message: {user_message}")
        travel_intent = analyze_travel_intent_with_llama(user_message)

        destination = travel_intent.get("destination") or ""

        # 🔧 Normalisation des nombres pour éviter True/False -> 1/0
        def parse_int(value, default=None, minimum=1):
            try:
                if isinstance(value, bool):
                    return default
                if isinstance(value, (int, float)):
                    iv = int(value)
                else:
                    s = str(value).strip()
                    if not s:
                        return default
                    # retirer unités éventuelles (dt, €, pers, nuits)
                    s = re.sub(r"[^0-9]", "", s)
                    if not s:
                        return default
                    iv = int(s)
                if iv < minimum:
                    return minimum
                return iv
            except Exception:
                return default

        budget = parse_int(travel_intent.get("budget"), default=100, minimum=1)
        duree = parse_int(travel_intent.get("duree"), default=1, minimum=1)
        personnes = parse_int(travel_intent.get("personnes"), default=2, minimum=1)

        print(f"🌐 Préparation d'offres pour {destination}...")
        annonces = scrape_real_travel_offers(destination, budget, personnes=personnes)
        print(f"✅ {len(annonces)} annonces trouvées")

        print("💬 Génération réponse utilisateur...")
        if FREE_MODE or not LLAMA_DETECTED:
            if destination:
                ai_response = (
                    f"Super choix ! Je te propose des pistes pour {destination}. "
                    f"Budget ~{budget} DT/nuit, durée {duree} nuit(s) pour {personnes} pers. "
                    f"J'ai listé {len(annonces)} options; dis-moi tes dates pour affiner."
                )
            else:
                ai_response = (
                    f"J'ai listé des liens utiles pour commencer ta recherche. "
                    f"Dis-moi une destination, des dates et un budget pour cibler les résultats."
                )
        else:
            prompt_reponse = f'''Tu es un assistant voyage expert. Fais un résumé concis.

Demande: "{user_message}"
Destination: {destination}
Budget: {budget} DT
Durée: {duree} nuit(s) | Personnes: {personnes}
Nombre d'offres trouvées: {len(annonces)}

Fais un résumé friendly en 1-2 phrases maximum.'''
            ai_response = call_llama_api(prompt_reponse)
            if isinstance(ai_response, str) and ai_response.startswith("[Simulation]"):
                if destination:
                    ai_response = (
                        f"Voici quelques pistes pour {destination}. "
                        f"J'ai trouvé {len(annonces)} options environ. "
                        f"Dis-moi tes dates et ton budget précis pour affiner."
                    )
                else:
                    ai_response = (
                        f"J'ai listé des liens utiles pour explorer des offres. "
                        f"Partage une destination, des dates et un budget pour des suggestions ciblées."
                    )

        response_data = {
            "ai_response": ai_response,
            "annonces": annonces,
            "detected_preferences": {
                "budget": budget,
                "destination": destination,
                "duree": duree,
                "personnes": personnes,
                "interests": travel_intent.get("interets", [])
            },
            "travel_intent": travel_intent,
            "search_metadata": {
                "destination": destination,
                "budget": budget,
                "results_count": len(annonces),
                "llama_used": LLAMA_DETECTED is not None,
                "timestamp": datetime.now().isoformat()
            }
        }

        return Response(response_data)

    except Exception as e:
        import traceback
        print(f"❌ Erreur endpoint: {e}")
        print(traceback.format_exc())
        # Retourner un code d'erreur approprié pour que le frontend puisse le détecter
        return Response({
            "ai_response": f"Désolé, une erreur s'est produite lors du traitement de votre demande. {str(e)}",
            "annonces": generate_fallback_offers("Tunis", 100),
            "error": str(e),
            "detected_preferences": {},
            "travel_intent": {},
            "search_metadata": {
                "destination": "Tunis",
                "budget": 100,
                "results_count": 0,
                "llama_used": False,
                "timestamp": datetime.now().isoformat()
            }
        }, status=500)

# -----------------------------
# AUTRES VUES
# -----------------------------
def home(request):
    return HttpResponse(f"""
    <h1>🚀 App-Travell - Métamoteur Voyage</h1>
    <p>Backend Django avec Llama API + Scraping réel</p>
    <p><strong>URL Llama détectée:</strong> {LLAMA_DETECTED or 'Aucune (mode simulation)'}</p>
    <ul>
        <li><a href="/api/health/">Health Check</a></li>
        <li>Endpoint Chat: POST /api/chat/</li>
        <li>Endpoint Intelligent Travel Chat: POST /api/intelligent_travel_chat/</li>
    </ul>
    """)

@api_view(["GET"])
def recommendations(request):
    return Response({
        "message": "Endpoint recommandations opérationnel."
    })

@api_view(["GET"])
def destinations_list(request):
    try:
        qs = Destination.objects.all()[:10]
        data = [{"id": d.id, "title": d.title, "city": d.city.name if d.city else "N/A"} for d in qs]
        return Response(data)
    except Exception as e:
        print(f"❌ Erreur destinations: {e}")
        return Response([])

@api_view(["GET"])
def collect_external_data(request):
    return Response({
        "message": "Endpoint collect_external_data opérationnel."
    })

# -----------------------------
# SERIALIZERS
# -----------------------------
class CityInlineSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

class DestinationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    avg_price_level = serializers.IntegerField(allow_null=True)
    popularity_score = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    image_url = serializers.CharField(allow_null=True)
    city = CityInlineSerializer()