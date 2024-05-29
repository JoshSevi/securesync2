import time
from firebase_config import get_database_reference

db_ref = get_database_reference()

def enroll_user():
    try:
        name = input('Enter name: ')
        
        ref = db_ref.child('users')
        users = ref.get()

        for user_id, user_data in users.items():
            if user_data['name'].lower() == name.lower():
                print(f'User {name} already enrolled.')
                return

        new_user_ref = ref.push()
        new_user_ref.set({
            'name': name
        })

        print(f'User {name} enrolled successfully.')

    except Exception as e:
        print('Failed to enroll user!')
        print('Exception message: ' + str(e))

def verify_user_for_attendance():
    try:
        name = input('Enter name for attendance verification: ')
        
        ref = db_ref.child('users')
        users = ref.get()

        matched_user = None
        for user_id, user_data in users.items():
            if user_data['name'].lower() == name.lower():
                matched_user = (user_id, user_data['name'])
                break

        if matched_user:
            user_id, user_name = matched_user
            current_date = time.strftime('%Y-%m-%d')
            current_time = time.strftime('%H:%M:%S')

            attendance_ref = db_ref.child('attendance')
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
            print('User not found.')

    except Exception as e:
        print('Failed to verify user!')
        print('Exception message: ' + str(e))

def update_user_name():
    old_name = input("Enter current name: ")
    new_name = input("Enter new name: ")
    try:
        ref = db_ref.child('users')
        users = ref.get()

        user_id_to_update = None
        for user_id, user_data in users.items():
            if user_data['name'].lower() == old_name.lower():
                user_id_to_update = user_id
                break

        if user_id_to_update:
            ref.child(user_id_to_update).update({'name': new_name})
            print(f'Name updated from {old_name} to {new_name} successfully.')
        else:
            print('Name not found.')

    except Exception as e:
        print('Failed to update name!')
        print('Exception message: ' + str(e))

def delete_user():
    name = input("Enter name to delete: ")
    try:
        ref = db_ref.child('users')
        users = ref.get()

        user_id_to_delete = None
        for user_id, user_data in users.items():
            if user_data['name'].lower() == name.lower():
                user_id_to_delete = user_id
                break

        if user_id_to_delete:
            ref.child(user_id_to_delete).delete()
            print(f'User {name} deleted successfully.')
        else:
            print('Name not found.')

    except Exception as e:
        print('Failed to delete user!')
        print('Exception message: ' + str(e))

def view_users():
    try:
        ref = db_ref.child('users')
        users = ref.get()

        if not users:
            print('No users enrolled.')
        else:
            print('Enrolled users:')
            for user_data in users.values():
                print(user_data['name'])

    except Exception as e:
        print('Failed to fetch users!')
        print('Exception message: ' + str(e))

def main():
    while True:
        print("\n1. Enroll User")
        print("2. Verify User for Attendance")
        print("3. Update User Name")
        print("4. Delete User")
        print("5. View Enrolled Users")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            enroll_user()
        elif choice == '2':
            verify_user_for_attendance()
        elif choice == '3':
            update_user_name()
        elif choice == '4':
            delete_user()
        elif choice == '5':
            view_users()
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
