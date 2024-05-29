import time
from firebase_config import get_database_reference

db_ref = get_database_reference()


import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Initialize Firebase Admin SDK
cred = credentials.Certificate("path/to/serviceAccountKey.json") # Update with your own service account key
firebase_admin.initialize_app(cred)

# Get a reference to the Firebase Realtime Database
db_ref = db.reference()

def store_data(data):
    timestamp = int(time.time() * 1000) # Convert current time to milliseconds
    data_to_store = {
        'timestamp': timestamp,
        'data': data
    }
    db_ref.push(data_to_store) # Push data to the database

# Function to get user input
def get_user_input():
    temperature = float(input("Enter temperature: "))
    humidity = float(input("Enter humidity: "))
    sensor_id = input("Enter sensor ID: ")
    return {'temperature': temperature, 'humidity': humidity, 'sensor_id': sensor_id}

# Main function
def main():
    while True:
        data_to_store = get_user_input()
        store_data(data_to_store)
        print("Data stored successfully.")
        continue_input = input("Do you want to continue? (yes/no): ")
        if continue_input.lower() != 'yes':
            break

if __name__ == "__main__":
    main()
