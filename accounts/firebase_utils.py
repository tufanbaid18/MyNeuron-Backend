import requests
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

FIREBASE_DB_URL = "https://notification-myneuron-default-rtdb.firebaseio.com"

def push_notification_to_firebase(user_id, data):
    try:
        url = f"{FIREBASE_DB_URL}/notifications/{user_id}.json"

        payload = {
            "action": data.get("action"),
            "actor": data.get("actor"),
            "post": data.get("post"),
            "handshake": data.get("handshake"),
            "created_at": timezone.now().isoformat(),
            "is_read": False,
        }

        response = requests.post(url, json=payload, timeout=3)
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error("Firebase push failed: %s", e)
        return None
