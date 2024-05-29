import firebase_admin
from firebase_admin import credentials

# Path to the service account key JSON file
SERVICE_ACCOUNT_KEY_PATH = '/serviceAccountKey.json'

# Initialize the app with a service account, granting admin privileges
cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://<your-database-name>.firebaseio.com'
})
