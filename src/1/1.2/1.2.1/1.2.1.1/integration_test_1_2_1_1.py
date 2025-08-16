import unittest
from unittest.mock import patch, Mock
import os
import requests
from urllib.parse import urlparse, parse_qs

# Import the module containing the code to be tested.
# This assumes the provided implementation is in a file named 'subtask_1_2_1_1_2.py'
import subtask_1_2_1_1_2 as oauth_flow

class TestOAuthFlowIntegration(unittest.TestCase):

    def setUp(self):
        """Set up a clean environment for each test."""
        self.test_client_id = "test_client_id_123"
        self.test_client_secret = "test_client_secret_xyz"
        
        # We patch the module's constants directly to ensure our test values are used.
        # This is more reliable than patching os.environ after the module has already been imported.
        oauth_flow.CLIENT_ID = self.test_client_id
        oauth_flow.CLIENT_SECRET = self.test_client_secret
        oauth_flow.REDIRECT_URI = "https://testapp.com/callback"
        oauth_flow.AUTHORIZATION_URL = "https://fake-provider.com/auth"
        oauth_flow.TOKEN_URL = "https://fake-provider.com/token"
        oauth_flow.SCOPE = "read write"
        
        # Clear the global session storage before each test to ensure isolation.
        oauth_flow._session_storage.clear()

    def tearDown(self):
        """Clean up after each test."""
        oauth_flow._session_storage.clear()

    def test_get_authorization_url_structure_and_state_storage(self):
        """
        Tests if get_authorization_url generates a correctly formatted URL
        and properly stores the generated state in the session storage.
        """
        auth_url, state = oauth_flow.get_authorization_url()

        # 1. Verify a non-empty state string was generated and returned.
        self.assertIsInstance(state, str)
        self.assertGreater(len(state), 10)

        # 2. Verify the generated state was stored in the module's session storage.
        self.assertIn('oauth_state', oauth_flow._session_storage)
        self.assertEqual(oauth_flow._session_storage['oauth_state'], state)

        # 3. Verify the structure and parameters of the generated URL.
        parsed_url = urlparse(auth_url)
        self.assertEqual(f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}", oauth_flow.AUTHORIZATION_URL)
        
        query_params = parse_qs(parsed_url.query)
        self.assertEqual(query_params['client_id'][0], self.test_client_id)
        self.assertEqual(query_params['redirect_uri'][0], oauth_flow.REDIRECT_URI)
        self.assertEqual(query_params['response_type'][0], 'code')
        self.assertEqual(query_params['scope'][0], oauth_flow.SCOPE)
        self.assertEqual(query_params['state'][0], state)

    @patch('subtask_1_2_1_1_2.requests.post')
    def test_integration_successful_token_exchange(self, mock_post):
        """
        Tests the complete successful flow: generating a state, then using that
        state to exchange a code for a token.
        """
        # Step 1: Generate the authorization URL and get the state, which is stored internally.
        _, original_state = oauth_flow.get_authorization_url()
        self.assertIn('oauth_state', oauth_flow._session_storage, "State should be in session after generating URL")

        # Step 2: Configure the mock for a successful response from the token endpoint.
        mock_response = Mock()
        mock_response.status_code = 200
        expected_token_data = {
            "access_token": "mock_access_token_12345",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "read write"
        }
        mock_response.json.return_value = expected_token_data
        mock_response.raise_for_status.return_value = None 
        mock_post.return_value = mock_response

        # Step 3: Call exchange_code_for_token with valid parameters.
        auth_code = "valid_auth_code_from_provider"
        token_info = oauth_flow.exchange_code_for_token(auth_code, original_state)

        # Step 4: Assert the results.
        self.assertIsNotNone(token_info)
        self.assertEqual(token_info, expected_token_data)

        # Verify that the session state was consumed and cleared after a successful exchange.
        self.assertNotIn('oauth_state', oauth_flow._session_storage)

        # Verify that the HTTP POST request was made with the correct parameters.
        mock_post.assert_called_once()
        call_args, call_kwargs = mock_post.call_args
        self.assertEqual(call_args[0], oauth_flow.TOKEN_URL)
        expected_payload = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': oauth_flow.REDIRECT_URI,
            'client_id': self.test_client_id,
            'client_secret': self.test_client_secret
        }
        self.assertEqual(call_kwargs['data'], expected_payload)

    @patch('subtask_1_2_1_1_2.requests.post')
    def test_exchange_fails_with_mismatched_state(self, mock_post):
        """
        Tests that the token exchange is aborted if the provided state does not
        match the one in the session, preventing CSRF.
        """
        oauth_flow.get_authorization_url() # This sets a state in the session.
        
        # Attempt the exchange with a completely different, incorrect state.
        token_info = oauth_flow.exchange_code_for_token("any_code", "tampered_state_value")
        
        self.assertIsNone(token_info, "Function should return None for invalid state")
        mock_post.assert_not_called(), "External HTTP request should not be made if state is invalid"
        self.assertNotIn('oauth_state', oauth_flow._session_storage, "State should be cleared even on failure")

    @patch('subtask_1_2_1_1_2.requests.post')
    def test_exchange_fails_with_no_session_state(self, mock_post):
        """
        Tests that the token exchange fails if no state exists in the session,
        simulating an expired or lost user session.
        """
        # Ensure the session storage is empty.
        self.assertNotIn('oauth_state', oauth_flow._session_storage)

        # Attempt the exchange.
        token_info = oauth_flow.exchange_code_for_token("any_code", "any_state_value")

        self.assertIsNone(token_info)
        mock_post.assert_not_called()

    @patch('subtask_1_2_1_1_2.requests.post')
    def test_exchange_handles_provider_http_error(self, mock_post):
        """
        Tests that the function returns None when the provider returns an HTTP error (e.g., 400 Bad Request).
        """
        _, original_state = oauth_flow.get_authorization_url()

        # Configure mock to simulate an HTTP error.
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = '{"error": "invalid_grant", "error_description": "The authorization code is invalid or expired."}'
        # The raise_for_status method is key to triggering the exception handling in the code.
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_post.return_value = mock_response

        token_info = oauth_flow.exchange_code_for_token("bad_code", original_state)
        
        self.assertIsNone(token_info)
        mock_post.assert_called_once()
        self.assertNotIn('oauth_state', oauth_flow._session_storage, "State should be cleared on failure")

    @patch('subtask_1_2_1_1_2.requests.post')
    def test_exchange_handles_malformed_success_response(self, mock_post):
        """
        Tests that the function returns None if the provider gives a 200 OK response
        but the JSON body is missing the required 'access_token' key.
        """
        _, original_state = oauth_flow.get_authorization_url()

        # Configure mock for a 200 OK response with a malformed body.
        mock_response = Mock()
        mock_response.status_code = 200
        malformed_data = {"token_type": "Bearer", "details": "Token not generated"}
        mock_response.json.return_value = malformed_data
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        token_info = oauth_flow.exchange_code_for_token("any_code", original_state)
        
        self.assertIsNone(token_info)
        mock_post.assert_called_once()
        self.assertNotIn('oauth_state', oauth_flow._session_storage, "State should be cleared on failure")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)