import firebase_admin
from firebase_admin import credentials, db
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

cred = credentials.Certificate("notification-myneuron-firebase-adminsdk-fbsvc-4d64bbfcfa.json")

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://notification-myneuron-default-rtdb.firebaseio.com/"
})
