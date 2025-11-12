# chatbot/chatbot_service.py
import requests, os, sys
from pathlib import Path

# ---- Make sure we can find config.py ----
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from config import BACKEND_URL  # local import works now

def send_message_to_backend(message: str) -> str:
    try:
        response = requests.post(BACKEND_URL, json={"message": message})
        if response.status_code == 200:
            return response.json().get("reply", "No reply received.")
        return f"⚠️ Error {response.status_code}: {response.text}"
    except Exception:
        return f"🧠 Backend not available right now.\n\n(Demo reply) You said: '{message}'"
