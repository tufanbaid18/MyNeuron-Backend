import requests
from django.conf import settings
from django.utils import timezone

# Firebase Realtime DB URL
FIREBASE_DB_URL = "https://notification-myneuron-default-rtdb.firebaseio.com"

def push_notification_to_firebase(user_id, data):
    """
    Pushes a notification to Firebase under the specific user node.
    """
    url = f"{FIREBASE_DB_URL}/notifications/{user_id}.json"

    payload = {
        "action": data.get("action"),
        "actor": data.get("actor"),
        "post": data.get("post"),
        "handshake": data.get("handshake"),
        "created_at": timezone.now().isoformat(),
        "is_read": False
    }

    response = requests.post(url, json=payload)

    print("🔥 Firebase push response:", response.text)
    return response.json()
