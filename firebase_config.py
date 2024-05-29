import firebase_admin
from firebase_admin import credentials, db

# Path to the service account key JSON file
SERVICE_ACCOUNT_KEY_PATH = 'sync-24-firebase-adminsdk-ggv97-9cc2e3a145.json'

# Initialize the app with a service account, granting admin privileges
cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sync-24-default-rtdb.asia-southeast1.firebasedatabase.app'
})

# Provide a reference to the database
def get_database_reference():
    return db.reference()
