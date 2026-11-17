from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
import requests
import os
app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mon_code_123")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

def envoyer_message(numero_client, texte):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": numero_client,
        "type": "text",
        "text": {"body": texte}
    }
    r = requests.post(url, headers=headers, json=payload)
    print("Envoi:", r.status_code, r.text)
    return r

@app.route("/", methods=["GET"])
def accueil():
    return "Bot en ligne ✅"

@app.route("/webhook", methods=["GET"])
def verifier():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Token incorrect", 403

@app.route("/webhook", methods=["POST"])
def recevoir():
    data = request.get_json()
    print("Recu:", data)
    try:
        value = data['entry'][0]['changes'][0]['value']
        if 'messages' not in value:
            return jsonify({"status": "ok"}), 200

        message = value['messages'][0]
        numero_client = message['from']
        texte = message.get('text', {}).get('body', '').lower().strip()

        # --- SEULEMENT LES SALUTATIONS ---
        if texte in ["salut", "bonjour", "coucou", "yo", "cc", "hello", "bonsoir", "slt", "bjr"]:
            reponse = "Bonjour, bienvenue chez JM Services 👋\nComment je peux t'aider ?"
            envoyer_message(numero_client, reponse)

    except Exception as e:
        print("Erreur:", e)
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)