from flask import Flask, request, jsonify
from gpt4all import GPT4All

app = Flask(__name__)

# Chargement du modèle
print("🦙 Chargement du modèle Llama...")
try:
    model = GPT4All("Llama-3.2-1B-Instruct-Q4_0.gguf")
    print("✅ Modèle Llama chargé!")
except Exception as e:
    print(f"❌ Erreur chargement modèle: {e}")
    model = None

# ✅ C'EST CETTE ROUTE QUI DOIT ÊTRE BIEN ÉCRITE :
@app.route('/generate', methods=['POST'])  # ← NE PAS OUBLIER methods=['POST']
def generate():
    if model is None:
        return jsonify({"error": "Modèle non chargé"}), 500
    try:
        data = request.json
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 200)

        print(f"📨 Prompt reçu : {prompt}")
        response = model.generate(prompt, max_tokens=max_tokens)

        return jsonify({"text": response})

    except Exception as e:
        print(f"❌ Erreur génération : {e}")
        return jsonify({"error": str(e)}), 500

# Route de santé pour vérifier si le modèle est bien chargé
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "model_loaded": model is not None})

if __name__ == '__main__':
    print("🚀 Démarrage du serveur Llama sur http://0.0.0.0:8000...")
    app.run(port=8000, host='0.0.0.0', debug=True)


@app.route('/api/chat/', methods=['POST'])
def chat():
    data = request.get_json()
    prompt = data.get('message', '')  # ✅ prend tout le prompt
    print("Prompt reçu :", prompt)

    try:
        response = model.generate(prompt, max_tokens=200)
        return jsonify({
            "ai_response": response,
            "annonces": [],  # ← tu peux mettre des vraies annonces ici
            "detected_preferences": {}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
