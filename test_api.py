# test_api.py
import requests
import json
import time # Optional: Für kleine Pausen

# Die URL deines lokalen Servers
# WICHTIG: Diese muss zu dem passen, was dein app.py Server anzeigt (standardmäßig Port 5000)
API_URL = "http://localhost:5000/chatbot"

# Dies speichert den Konversationsverlauf, damit der Bot den Kontext behält
# Wird bei jeder Anfrage an das Backend gesendet
conversation_history = []

# Funktion zum Senden einer Nachricht an den Bot und Empfangen der Antwort
def send_message(message, history):
    # Die Daten, die an den Flask-Server gesendet werden
    payload = {
        "message": message,
        "history": history
    }
    # Die Header sagen dem Server, dass wir JSON senden
    headers = {'Content-Type': 'application/json'}

    try:
        # Sende die POST-Anfrage an deinen Bot
        response = requests.post(API_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status() # Löst einen HTTPError für schlechte Antworten (4xx oder 5xx) aus

        # Wenn die Anfrage erfolgreich war, gib die JSON-Antwort zurück
        return response.json()
    except requests.exceptions.ConnectionError:
        print("\n[FEHLER] Konnte keine Verbindung zum Server herstellen. Stelle sicher, dass 'app.py' läuft!")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\n[FEHLER] Ein Problem ist aufgetreten: {e}")
        return None

# Haupt-Chat-Schleife
print("Chatbot-Test gestartet. Gib 'exit' ein, um zu beenden.")
print("Bot: Hallo! Wie kann ich Ihnen heute bei Ihren Fragen zu KI-Chatbots und Sprachagenten helfen?")

while True:
    user_input = input("Du: ") # Warte auf Benutzereingabe
    if user_input.lower() == 'exit':
        break # Beende die Schleife, wenn der Benutzer 'exit' eingibt

    # Sende die Nachricht des Benutzers an den Bot und erhalte die Antwort
    result = send_message(user_input, conversation_history)

    if result:
        bot_response = result.get('response')
        # Aktualisiere den Konversationsverlauf mit der neuen Nachricht und der Bot-Antwort
        conversation_history = result.get('history')
        print(f"Bot: {bot_response}")
    else:
        # Wenn kein Ergebnis zurückkam (z.B. bei einem Verbindungsfehler)
        print("Konnte keine gültige Antwort vom Bot erhalten.")

    # time.sleep(0.5) # Optional: Kurze Pause für besseres Lesefluss

print("Chat beendet.")