import getpass
from database.session import get_db, init_db
import crud.user as user_crud

def main():
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    
    # initialise the DB (creates tables if they don't exist)
    init_db()
    
    with get_db() as conn:
        try:
            new_user = user_crud.create_user(conn, username, password)
            print(f"Success. User {new_user['username']} created")
        except Exception as e:
            print(f"Error creating user: {e}")

if __name__ == "__main__":
    main()
