import time
from pyfingerprint.pyfingerprint import PyFingerprint
import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase
cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sync-24-default-rtdb.asia-southeast1.firebasedatabase.app'
})

def get_fingerprint_template(f):
    try:
        print('Waiting for finger...')

        # Wait for finger to read
        while not f.readImage():
            pass

        # Converts read image to characteristics and stores it in charbuffer 1
        f.convertImage(0x01)

        # Remove finger and wait for the same finger again
        print('Remove finger...')
        time.sleep(2)
        print('Waiting for same finger again...')

        # Wait for finger to read again
        while not f.readImage():
            pass

        # Converts read image to characteristics and stores it in charbuffer 2
        f.convertImage(0x02)

        # Compares the charbuffers
        if f.compareCharacteristics() == 0:
            raise Exception('Fingers do not match.')

        # Downloads the characteristics of template
        template = f.downloadCharacteristics(0x01)

        return template

    except Exception as e:
        print('Failed to get fingerprint template!')
        print('Exception message: ' + str(e))
        return None

def enroll_user():
    try:
        f = PyFingerprint('/dev/ttyS0', 57600, 0xFFFFFFFF, 0x00000000)

        if not f.verifyPassword():
            raise ValueError('The fingerprint sensor password is incorrect!')

        template = get_fingerprint_template(f)
        if template is None:
            return

        ref = db.reference('users')
        users = ref.get()

        for user_id, user_data in users.items():
            stored_template = list(map(int, user_data['fingerprint_template'].strip('[]').split(', ')))
            f.uploadCharacteristics(0x01, stored_template)
            if f.compareCharacteristics() > 50:  # Similarity threshold
                print(f'Fingerprint already enrolled for {user_data["name"]}.')
                return

        name = input('Enter name: ')
        new_user_ref = ref.push()
        new_user_ref.set({
            'name': name,
            'fingerprint_template': str(template)
        })

        print(f'Fingerprint for {name} enrolled successfully.')

    except Exception as e:
        print('Failed to enroll user!')
        print('Exception message: ' + str(e))

def verify_fingerprint():
    try:
        f = PyFingerprint('/dev/ttyS0', 57600, 0xFFFFFFFF, 0x00000000)

        if not f.verifyPassword():
            raise ValueError('The fingerprint sensor password is incorrect!')

        print('Waiting for finger...')

        # Wait for finger to read
        while not f.readImage():
            pass

        # Converts read image to characteristics and stores it in charbuffer 1
        f.convertImage(0x01)

        ref = db.reference('users')
        users = ref.get()

        matched_user = None
        for user_id, user_data in users.items():
            stored_template = list(map(int, user_data['fingerprint_template'].strip('[]').split(', ')))
            f.uploadCharacteristics(0x02, stored_template)  # Compare with charbuffer 2
            if f.compareCharacteristics() > 50:  # Similarity threshold
                matched_user = (user_id, user_data['name'])
                break

        if matched_user:
            user_id, user_name = matched_user
            current_date = time.strftime('%Y-%m-%d')
            current_time = time.strftime('%H:%M:%S')

            attendance_ref = db.reference('attendance')
            attendance_records = attendance_ref.order_by_child('user_id').equal_to(user_id).get()

            time_out_recorded = False
            for record_id, record_data in attendance_records.items():
                if record_data['date'] == current_date and 'time_out' not in record_data:
                    attendance_ref.child(record_id).update({'time_out': current_time})
                    print(f'Time-out recorded for {user_name} at {current_time}.')
                    time_out_recorded = True
                    break

            if not time_out_recorded:
                attendance_ref.push({
                    'user_id': user_id,
                    'date': current_date,
                    'time_in': current_time
                })
                print(f'Time-in recorded for {user_name} at {current_time}.')

        else:
            print('Unrecognized fingerprint.')

    except Exception as e:
        print('Failed to verify fingerprint!')
        print('Exception message: ' + str(e))

def update_fingerprint():
    name = input("Enter name to update fingerprint: ")
    try:
        f = PyFingerprint('/dev/ttyS0', 57600, 0xFFFFFFFF, 0x00000000)

        if not f.verifyPassword():
            raise ValueError('The fingerprint sensor password is incorrect!')

        template = get_fingerprint_template(f)
        if template is None:
            return

        ref = db.reference('users')
        users = ref.get()

        user_id_to_update = None
        for user_id, user_data in users.items():
            if user_data['name'] == name:
                user_id_to_update = user_id
                break

        if user_id_to_update:
            ref.child(user_id_to_update).update({'fingerprint_template': str(template)})
            print(f'Fingerprint for {name} updated successfully.')
        else:
            print('Name not found.')

    except Exception as e:
        print('Failed to update fingerprint!')
        print('Exception message: ' + str(e))

def delete_fingerprint():
    name = input("Enter name to delete fingerprint: ")
    try:
        ref = db.reference('users')
        users = ref.get()

        user_id_to_delete = None
        for user_id, user_data in users.items():
            if user_data['name'] == name:
                user_id_to_delete = user_id
                break

        if user_id_to_delete:
            ref.child(user_id_to_delete).delete()
            print(f'Fingerprint for {name} deleted successfully.')
        else:
            print('Name not found.')

    except Exception as e:
        print('Failed to delete fingerprint!')
        print('Exception message: ' + str(e))

def view_fingerprints():
    try:
        ref = db.reference('users')
        users = ref.get()

        if not users:
            print('No fingerprints enrolled.')
        else:
            print('Enrolled fingerprints:')
            for user_data in users.values():
                print(user_data['name'])

    except Exception as e:
        print('Failed to fetch fingerprints!')
        print('Exception message: ' + str(e))

def main():
    while True:
        print("\n1. Enroll Fingerprint")
        print("2. Verify Fingerprint for Attendance")
        print("3. Update Fingerprint")
        print("4. Delete Fingerprint")
        print("5. View Enrolled Fingerprints")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            enroll_user()
        elif choice == '2':
            verify_fingerprint()
        elif choice == '3':
            update_fingerprint()
        elif choice == '4':
            delete_fingerprint()
        elif choice == '5':
            view_fingerprints()
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
