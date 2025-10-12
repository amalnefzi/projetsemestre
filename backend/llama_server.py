# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import sys
import io

# Fix encodage Windows pour les emojis
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ Décommente cette ligne
from gpt4all import GPT4All
import json
import re

app = Flask(__name__)
CORS(app)  # ✅ Active CORS pour autoriser les requêtes depuis React

# Chargement du modèle
print("Chargement du modèle Llama...")
try:
    model = GPT4All("Llama-3.2-1B-Instruct-Q4_0.gguf")
    print("Modèle Llama charge!")
except Exception as e:
    print(f"Erreur chargement modèle: {e}")
    model = None

# Historique des conversations (en mémoire)
conversation_history = {}

def extract_preferences(message):
    """Extrait les préférences utilisateur du message"""
    preferences = {
        "budget": None,
        "interests": [],
        "destination": None
    }
    
    message_lower = message.lower()
    
    # Extraction du budget
    budget_keywords = {
        "pas cher": "economique",
        "economique": "economique",
        "petit budget": "economique",
        "luxe": "luxe",
        "premium": "luxe",
        "moyen": "moyen",
        "standard": "moyen"
    }
    for keyword, budget_type in budget_keywords.items():
        if keyword in message_lower:
            preferences["budget"] = budget_type
            break
    
    # Extraction des intérêts
    interests_keywords = {
        "plage": "plage",
        "mer": "plage",
        "culture": "culture",
        "musee": "culture",
        "histoire": "culture",
        "nature": "nature",
        "randonnee": "nature",
        "montagne": "nature",
        "aventure": "aventure",
        "sport": "aventure"
    }
    for keyword, interest in interests_keywords.items():
        if keyword in message_lower:
            if interest not in preferences["interests"]:
                preferences["interests"].append(interest)
    
    # Extraction de destination
    destinations = ["paris", "rome", "london", "barcelone", "new york", "tokyo", "dubai", "marrakech", "istanbul", "tunis"]
    for dest in destinations:
        if dest in message_lower:
            preferences["destination"] = dest.capitalize()
            break
    
    return preferences

def build_smart_prompt(user_message, user_id):
    """Construit un prompt intelligent avec contexte"""
    
    # Récupérer l'historique
    history = conversation_history.get(user_id, [])
    
    # Extraire les préférences
    prefs = extract_preferences(user_message)
    
    # Construire le contexte
    context = "Tu es un assistant de voyage amical et expert.\n"
    context += "Regles:\n"
    context += "- Reponds de maniere conversationnelle et naturelle\n"
    context += "- Pose des questions pour mieux comprendre les besoins\n"
    context += "- Sois enthousiaste et utile\n"
    context += "- Garde tes reponses courtes (2-3 phrases max)\n\n"
    
    # Ajouter l'historique récent (3 derniers messages)
    if history:
        context += "Historique recent:\n"
        for msg in history[-3:]:
            context += f"- {msg['role']}: {msg['content']}\n"
        context += "\n"
    
    # Ajouter les préférences détectées
    if prefs["budget"] or prefs["interests"] or prefs["destination"]:
        context += "Preferences detectees:\n"
        if prefs["budget"]:
            context += f"- Budget: {prefs['budget']}\n"
        if prefs["interests"]:
            context += f"- Interets: {', '.join(prefs['interests'])}\n"
        if prefs["destination"]:
            context += f"- Destination: {prefs['destination']}\n"
        context += "\n"
    
    # Message actuel
    context += f"Utilisateur: {user_message}\nAssistant:"
    
    return context, prefs

@app.route('/api/chat/', methods=['POST'])
def chat():
    """Route principale du chat avec extraction intelligente"""
    if model is None:
        return jsonify({"error": "Modele non charge"}), 500
    
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        user_id = data.get('user_id', 1)
        
        print(f"Message recu (user {user_id}): {user_message}")
        
        # Construire le prompt intelligent
        prompt, preferences = build_smart_prompt(user_message, user_id)
        
        print("Prompt construit")
        
        # Générer la réponse
        ai_response = model.generate(prompt, max_tokens=150, temp=0.7)
        ai_response = ai_response.strip()
        
        print(f"Reponse IA: {ai_response}")
        
        # Mettre à jour l'historique
        if user_id not in conversation_history:
            conversation_history[user_id] = []
        
        conversation_history[user_id].append({
            "role": "Utilisateur",
            "content": user_message
        })
        conversation_history[user_id].append({
            "role": "Assistant",
            "content": ai_response
        })
        
        # Limiter l'historique à 10 messages
        if len(conversation_history[user_id]) > 10:
            conversation_history[user_id] = conversation_history[user_id][-10:]
        
        return jsonify({
            "ai_response": ai_response,
            "annonces": [],
            "detected_preferences": preferences
        })
        
    except Exception as e:
        print(f"Erreur: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Vérification santé du serveur"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "active_conversations": len(conversation_history)
    })

@app.route('/reset', methods=['POST'])
def reset_conversation():
    """Réinitialiser une conversation"""
    data = request.get_json()
    user_id = data.get('user_id', 1)
    
    if user_id in conversation_history:
        del conversation_history[user_id]
    
    return jsonify({"status": "reset", "user_id": user_id})

if __name__ == '__main__':
    print("Serveur Llama demarre sur http://0.0.0.0:8000")
    print("Endpoints disponibles:")
    print("   - POST /api/chat/ : Chat principal")
    print("   - GET /health : Verification sante")
    print("   - POST /reset : Reinitialiser conversation")
    app.run(port=8000, host='0.0.0.0', debug=True)