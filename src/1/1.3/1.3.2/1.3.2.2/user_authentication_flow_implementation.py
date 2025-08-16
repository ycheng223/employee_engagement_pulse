import hashlib
import getpass

def user_authentication_flow():
    """
    Manages a simple user authentication flow including registration,
    login, logout, and access to a protected area.
    """
    # In-memory storage for users: {username: hashed_password}
    users = {}
    current_user = None

    def hash_password(password):
        """Hashes a password using SHA-256 for secure storage."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user():
        """Handles new user registration."""
        nonlocal users
        print("\n--- Register New User ---")
        username = input("Enter a username: ").lower()

        if username in users:
            print("Username already exists. Please try a different one.")
            return
        
        if not username or " " in username:
            print("Username cannot be empty or contain spaces.")
            return

        password = getpass.getpass("Enter a password: ")
        if len(password) < 4:
            print("Password is too short. Must be at least 4 characters.")
            return
            
        users[username] = hash_password(password)
        print(f"User '{username}' registered successfully!")

    def login_user():
        """Handles user login and session management."""
        nonlocal current_user
        if current_user:
            print(f"You are already logged in as {current_user}.")
            return

        print("\n--- User Login ---")
        username = input("Username: ").lower()
        password = getpass.getpass("Password: ")

        stored_hash = users.get(username)
        entered_hash = hash_password(password)

        if stored_hash and stored_hash == entered_hash:
            current_user = username
            print(f"\nWelcome, {username}! Login successful.")
        else:
            print("Invalid username or password.")

    def logout_user():
        """Logs out the current user."""
        nonlocal current_user
        if current_user:
            print(f"Logging out {current_user}.")
            current_user = None
        else:
            print("You are not currently logged in.")

    def access_protected_area():
        """A dummy function for a resource that requires login."""
        if current_user:
            print(f"\n--- Welcome to the Protected Area, {current_user}! ---")
            print("You have access to exclusive content.")
        else:
            print("\nAccess denied. Please log in to view this content.")

    # Main application loop
    while True:
        print("\n===============================")
        if current_user:
            print(f"Logged in as: {current_user}")
        else:
            print("Status: Not logged in")
        print("===============================")
        print("1. Register")
        print("2. Login")
        print("3. Access Protected Area")
        print("4. Logout")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            register_user()
        elif choice == '2':
            login_user()
        elif choice == '3':
            access_protected_area()
        elif choice == '4':
            logout_user()
        elif choice == '5':
            print("Exiting application.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")