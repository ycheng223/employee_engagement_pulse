import functools

# In a real application, this would be a database table.
# Passwords should always be hashed, never stored as plain text.
_USERS = {
    'manager_a': {'password': 'password123', 'role': 'manager'},
    'employee_b': {'password': 'password456', 'role': 'employee'},
}

def authenticate(username, password):
    """
    Performs authentication for a given user.

    Args:
        username (str): The username to authenticate.
        password (str): The password to check.

    Returns:
        dict: The user object if authentication is successful, otherwise None.
    """
    user_data = _USERS.get(username)
    if user_data and user_data['password'] == password:
        # In a real app, you'd verify a hashed password here.
        # Return a copy to avoid modifying the original data store.
        return {'username': username, 'role': user_data['role']}
    return None

def manager_authorization_required(func):
    """
    Decorator to ensure a user has the 'manager' role.

    This decorator assumes the authenticated user object is passed as the first
    positional argument to the decorated function.
    """
    @functools.wraps(func)
    def wrapper(user, *args, **kwargs):
        """
        Wrapper function that checks for manager role before executing the function.

        Args:
            user (dict): The authenticated user object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            PermissionError: If the user is not authenticated or not a manager.
        """
        if user and user.get('role') == 'manager':
            return func(user, *args, **kwargs)
        else:
            raise PermissionError("Access denied: Manager role required.")
    return wrapper

@manager_authorization_required
def access_sensitive_manager_dashboard(user, dashboard_section):
    """
    An example function that requires manager authorization to access.
    
    Args:
        user (dict): The authenticated user object (provided by the decorator).
        dashboard_section (str): The specific section of the dashboard to access.

    Returns:
        str: A success message indicating access was granted.
    """
    return (
        f"User '{user['username']}' successfully accessed "
        f"the '{dashboard_section}' section of the manager dashboard."
    )