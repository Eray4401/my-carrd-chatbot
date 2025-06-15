# app.py
from flask import Flask, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv
from flask_cors import CORS, cross_origin # Diese Zeile hinzufügen für CORS

# Lade Umgebungsvariablen aus der .env-Datei
# Stellt sicher, dass dein OPENAI_API_KEY aus der .env-Datei geladen wird
load_dotenv()

app = Flask(__name__)
# CORS für alle Routen aktivieren
# Dies ist notwendig, damit dein Frontend (Carrd) auf dein Backend zugreifen kann,
# da sie auf verschiedenen Domänen liegen werden.
CORS(app, resources={r"/chatbot": {"origins": "https://www.deinaiagent.de", "methods": ["GET", "HEAD", "POST", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})

# Initialisiere den OpenAI Client mit deinem API-Key
# Der API-Key wird aus der Umgebungsvariablen geladen (dank load_dotenv())
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Diese Route empfängt die Nachrichten von deinem Frontend (Web-Chat-Widget)
@app.route('/chatbot', methods=['POST', 'OPTIONS'])
def chatbot_response():
    # FÜGE DIESEN BLOCK HIER EIN:
    if request.method == 'OPTIONS':
        # Flask-CORS sollte die Header setzen, wir geben nur einen 200 OK zurück
        return '', 200
    # AB HIER GEHT DEIN BESTEHENDER CODE WEITER:
    data = request.json
    user_message = data.get('message')
    conversation_history = data.get('history', [])
   

    # Überprüfe, ob eine Nachricht gesendet wurde
    if not user_message:
        return jsonify({'response': 'Nachricht fehlt.'}), 400

    # Füge die aktuelle Benutzernachricht zum Verlauf hinzu
    # Dieser Verlauf wird für den Kontext an OpenAI gesendet
    conversation_history.append({"role": "user", "content": user_message})

    # !!! WICHTIGER TEIL: Der "System"-Prompt !!!
    # Dieser Prompt gibt dem KI-Modell Anweisungen, wie es sich verhalten und welche Art von Antworten es geben soll.
    # PASSE DIESEN TEXT AN DEINE SPEZIFISCHEN DIENSTLEISTUNGEN UND FIRMENNAMEN AN!
    system_prompt = {
        "role": "system",
        "content": (
            "Du bist ein freundlicher, professioneller und hilfsbereiter KI-Assistent. "
            "Deine Hauptaufgabe ist es, detaillierte und präzise Informationen zu "
            "KI-Chatbots und KI-Sprachagenten zu liefern, die von 'Dein Ai Agent' " # <-- HIER DEINEN FIRMENNAMEN EINTRAGEN!
            "angeboten werden. Erkläre die Vorteile und Anwendungsfälle unserer Dienste. "
            "Sei spezifisch und fokussiert auf unsere Angebote. "
            "Frage nach dem konkreten Interesse des Nutzers, z.B. 'Sind Sie an einer kostenlosen Demo interessiert?' "
            "Wenn eine Frage nicht direkt deine Dienstleistungen betrifft, leite freundlich zu passenden Abschnitten auf der Webseite weiter oder biete an, eine Kontaktanfrage zu vermitteln. "
            "Vermeide es, zu lange Antworten zu geben oder zu philosophieren. Halte dich an Fakten über unsere Produkte."
        )
    }

    # Baue die vollständige Nachrichtenliste für die OpenAI API auf
    # Der System-Prompt kommt immer zuerst, gefolgt vom bisherigen Konversationsverlauf.
    messages_for_openai = [system_prompt] + conversation_history

    try:
        # Sende die Anfrage an die OpenAI Chat Completions API
        # 'model': Wähle das gewünschte Modell (gpt-4o ist aktuell, gpt-3.5-turbo ist günstiger)
        # 'messages': Die Liste der Nachrichten, die den Kontext für das Modell bilden.
        # 'max_tokens': Begrenzt die maximale Länge der generierten Antwort des Bots (optional, aber empfohlen zur Kostenkontrolle und Prägnanz).
        # 'temperature': Kontrolliert die Kreativität/Zufälligkeit der Antwort (0.0 = sehr präzise/deterministisch, 1.0 = kreativer).
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=messages_for_openai,
            max_tokens=300,
            temperature=0.7
        )

        # Extrahiere die generierte Antwort des Bots aus der API-Antwort
        bot_response = response.choices[0].message.content

        # Füge die Bot-Antwort zum Verlauf hinzu, damit sie im nächsten Gesprächsschritt als Kontext dient
        conversation_history.append({"role": "assistant", "content": bot_response})

        # Sende die Antwort des Bots und den aktualisierten Verlauf zurück an das Frontend
        return jsonify({'response': bot_response, 'history': conversation_history})

    except Exception as e:
        # Fange potenzielle Fehler beim API-Aufruf ab und gib eine Fehlermeldung zurück
        print(f"Fehler bei OpenAI API-Aufruf: {e}")
        return jsonify({
            'response': "Entschuldigung, es ist ein technisches Problem aufgetreten. Bitte versuchen Sie es später erneut.",
            'history': conversation_history
        }), 500 # Sende einen HTTP 500 Fehlerstatus

# Startet den Flask-Server, wenn die Datei direkt ausgeführt wird
if __name__ == '__main__':
    # 'debug=True' ist nur für die Entwicklung! Nicht in einer Produktionsumgebung verwenden.
    # 'port=5000' bedeutet, der Server wird auf Port 5000 deines lokalen Rechners laufen.
    app.run(debug=True, port=5000)