import unittest
from unittest.mock import patch
import io
import sys
import hashlib
import getpass

# Implementation provided for the task 'Frontend Development'
# Component: 1.3.2/1.3.2.2 User Authentication Flow
def user_authentication_flow():
    """
    Manages a simple user authentication flow by prompting for a username and password,
    hashing the password, and comparing it against a stored value.
    """
    # This is a placeholder for a real user database
    # In a real application, this would be a secure database lookup
    users = {
        "admin": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"  # SHA-256 for 'password'
    }

    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    # Hash the provided password using SHA-256
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Check if the username exists and the hashed password matches
    if username in users and users[username] == hashed_password:
        print("Login successful!")
        return True
    else:
        print("Login failed. Invalid username or password.")
        return False

# Comprehensive Integration Test for the User Authentication Flow
class TestUserAuthenticationIntegration(unittest.TestCase):
    """
    Integration test for the user_authentication_flow.
    This test suite verifies the complete authentication process from user input
    to the final output, ensuring all internal steps (input gathering, hashing,
    comparison) work together correctly. It uses mocking to simulate user
    interaction without requiring manual input.
    """

    def setUp(self):
        """Redirect stdout to capture print statements before each test."""
        self.held_stdout = sys.stdout
        sys.stdout = io.StringIO()

    def tearDown(self):
        """Restore stdout after each test."""
        sys.stdout = self.held_stdout

    @patch('getpass.getpass')
    @patch('builtins.input')
    def test_successful_login_flow(self, mock_input, mock_getpass):
        """
        Tests the complete authentication flow for a successful login.
        It simulates a user entering the correct username ('admin') and password ('password').
        The test verifies the function's return value and console output.
        """
        # Arrange: Configure mocks to simulate correct user input
        mock_input.return_value = 'admin'
        mock_getpass.return_value = 'password'

        # Act: Execute the function
        result = user_authentication_flow()

        # Assert: Check for successful outcome
        self.assertTrue(result, "Function should return True on successful login.")
        self.assertEqual(sys.stdout.getvalue().strip(), "Login successful!",
                         "Success message should be printed on successful login.")

        # Assert that input functions were called correctly
        mock_input.assert_called_once_with("Enter your username: ")
        mock_getpass.assert_called_once_with("Enter your password: ")

    @patch('getpass.getpass')
    @patch('builtins.input')
    def test_failed_login_with_wrong_password(self, mock_input, mock_getpass):
        """
        Tests the authentication flow for a login attempt with a correct username
        but an incorrect password. Verifies the failure return value and message.
        """
        # Arrange: Configure mocks with correct username and wrong password
        mock_input.return_value = 'admin'
        mock_getpass.return_value = 'wrongpassword'

        # Act: Execute the function
        result = user_authentication_flow()

        # Assert: Check for failed outcome
        self.assertFalse(result, "Function should return False on login failure.")
        self.assertEqual(sys.stdout.getvalue().strip(), "Login failed. Invalid username or password.",
                         "Failure message should be printed for wrong password.")

    @patch('getpass.getpass')
    @patch('builtins.input')
    def test_failed_login_with_wrong_username(self, mock_input, mock_getpass):
        """
        Tests the authentication flow for a login attempt with an incorrect username
        that does not exist in the user store.
        """
        # Arrange: Configure mocks with a non-existent username
        mock_input.return_value = 'not_a_user'
        mock_getpass.return_value = 'password'

        # Act: Execute the function
        result = user_authentication_flow()

        # Assert: Check for failed outcome
        self.assertFalse(result, "Function should return False for a non-existent user.")
        self.assertEqual(sys.stdout.getvalue().strip(), "Login failed. Invalid username or password.",
                         "Failure message should be printed for wrong username.")

    @patch('getpass.getpass')
    @patch('builtins.input')
    def test_failed_login_with_case_sensitive_username(self, mock_input, mock_getpass):
        """
        Tests that the username check is case-sensitive, which is the default
        behavior for dictionary key lookups in the implementation.
        """
        # Arrange: Configure mocks with a username with incorrect casing
        mock_input.return_value = 'Admin'  # 'admin' is the correct username
        mock_getpass.return_value = 'password'

        # Act: Execute the function
        result = user_authentication_flow()

        # Assert: Check for failed outcome due to case-sensitivity
        self.assertFalse(result, "Function should return False for a case-mismatched username.")
        self.assertEqual(sys.stdout.getvalue().strip(), "Login failed. Invalid username or password.",
                         "Failure message should be printed for case-sensitive username mismatch.")

    @patch('getpass.getpass')
    @patch('builtins.input')
    def test_failed_login_with_empty_credentials(self, mock_input, mock_getpass):
        """
        Tests the authentication flow with empty strings for both username and password,
        a realistic edge case for user input.
        """
        # Arrange: Configure mocks to return empty strings
        mock_input.return_value = ''
        mock_getpass.return_value = ''

        # Act: Execute the function
        result = user_authentication_flow()

        # Assert: Check for failed outcome
        self.assertFalse(result, "Function should return False for empty credentials.")
        self.assertEqual(sys.stdout.getvalue().strip(), "Login failed. Invalid username or password.",
                         "Failure message should be printed for empty credentials.")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)