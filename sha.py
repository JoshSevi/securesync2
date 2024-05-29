import time
from pyfingerprint.pyfingerprint import PyFingerprint
from firebase_config import get_database_reference

db_ref = get_database_reference()


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

        users_ref = db_ref.child('users')
        users = users_ref.get()

        if users:
            for user_id, user_data in users.items():
                stored_template = user_data.get('fingerprint_template')
                if stored_template:
                    # Compare fingerprints
                    if compare_fingerprints(template, stored_template):
                        print(f'Fingerprint already enrolled for {user_data["name"]}.')
                        return

        name = input('Enter name: ')
        new_user_data = {
            'name': name,
            'fingerprint_template': template
        }
        users_ref.push(new_user_data)

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

        users_ref = db_ref.child('users')
        users = users_ref.get()

        matched_user = None
        if users:
            for user_id, user_data in users.items():
                stored_template = user_data.get('fingerprint_template')
                if stored_template:
                    if compare_fingerprints(template, stored_template):
                        matched_user = user_data
                        break

        if matched_user:
            user_name = matched_user['name']
            current_date = time.strftime('%Y-%m-%d')
            current_time = time.strftime('%H:%M:%S')

            attendance_ref = db_ref.child('attendance')
            attendance_record = attendance_ref.order_by_child('user_id').equal_to(user_id).get()

            for record_id, record_data in attendance_record.items():
                if record_data['date'] == current_date and not record_data['time_out']:
                    attendance_ref.child(record_id).update({'time_out': current_time})
                    print(f'Time-out recorded for {user_name} at {current_time}.')
                    return

            new_attendance_data = {
                'user_id': user_id,
                'date': current_date,
                'time_in': current_time
            }
            attendance_ref.push(new_attendance_data)
            print(f'Time-in recorded for {user_name} at {current_time}.')

        else:
            print('Unrecognized fingerprint.')

    except Exception as e:
        print('Failed to verify fingerprint!')
        print('Exception message: ' + str(e))


def compare_fingerprints(template1, template2):
    # Your fingerprint comparison logic here
    pass


def update_fingerprint():
    name = input("Enter name to update fingerprint: ")
    try:
        f = PyFingerprint('/dev/ttyS0', 57600, 0xFFFFFFFF, 0x00000000)

        if not f.verifyPassword():
            raise ValueError('The fingerprint sensor password is incorrect!')

        template = get_fingerprint_template(f)
        if template is None:
            return

        users_ref = db_ref.child('users')
        users = users_ref.order_by_child('name').equal_to(name).get()

        if users:
            for user_id, user_data in users.items():
                users_ref.child(user_id).update({'fingerprint_template': template})
                print(f'Fingerprint for {name} updated successfully.')
                return
        else:
            print('Name not found.')

    except Exception as e:
        print('Failed to update fingerprint!')
        print('Exception message: ' + str(e))


def delete_fingerprint():
    name = input("Enter name to delete fingerprint: ")
    try:
        users_ref = db_ref.child('users')
        users = users_ref.order_by_child('name').equal_to(name).get()

        if users:
            for user_id, user_data in users.items():
                users_ref.child(user_id).delete()
                print(f'Fingerprint for {name} deleted successfully.')
                return
        else:
            print('Name not found.')

    except Exception as e:
        print('Failed to delete fingerprint!')
        print('Exception message: ' + str(e))


def view_fingerprints():
    try:
        users_ref = db_ref.child('users')
        users = users_ref.get()

        if users:
            print('Enrolled fingerprints:')
            for user_id, user_data in users.items():
                print(user_data['name'])
        else:
            print('No fingerprints enrolled.')

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
