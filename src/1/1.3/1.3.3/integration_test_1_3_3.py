import unittest
import json

# --- Component Implementations ---
# These are the "available implementations" for the integration test.

# 1. Database Layer (database.py)
# A simple in-memory data store to simulate a database.

class ChannelDatabase:
    """Simulates a key-value database for channel configurations."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChannelDatabase, cls).__new__(cls)
            cls._instance.clear()
        return cls._instance

    def get_channel(self, channel_id):
        """Retrieves a channel's config, returns a copy."""
        config = self._data.get(channel_id)
        return config.copy() if config else None

    def save_channel(self, channel_id, config_data):
        """Saves or updates a channel's config."""
        if not isinstance(config_data, dict):
            raise TypeError("config_data must be a dictionary")
        self._data[channel_id] = config_data.copy()
        return self.get_channel(channel_id)

    def delete_channel(self, channel_id):
        """Deletes a channel's config if it exists."""
        if channel_id in self._data:
            del self._data[channel_id]
            return True
        return False

    def get_all_channels(self):
        """Returns all channel configurations."""
        return self._data.copy()

    def clear(self):
        """Clears all data, for test purposes."""
        self._data = {}

# 2. Business Logic Layer (config_manager.py)
# Handles validation and orchestrates data flow between the API and Database.

class ConfigManager:
    """Manages channel configuration logic."""
    def __init__(self, db):
        self.db = db

    def _is_valid_config(self, config):
        """Basic validation for a channel config."""
        if not isinstance(config, dict):
            return False
        if "name" not in config or not isinstance(config["name"], str) or not config["name"].strip():
            return False
        if "topic" not in config or not isinstance(config["topic"], str):
            return False
        return True

    def get_channel_config(self, channel_id):
        """Fetches a channel config."""
        return self.db.get_channel(channel_id)

    def create_channel(self, channel_id, config_data):
        """Creates a new channel if it doesn't exist and data is valid."""
        if self.db.get_channel(channel_id):
            return None, "conflict"  # Channel already exists
        if not self._is_valid_config(config_data):
            return None, "bad_request"  # Invalid data
        
        created_config = self.db.save_channel(channel_id, config_data)
        return created_config, "created"

    def update_channel_config(self, channel_id, update_data):
        """Updates an existing channel's config."""
        existing_config = self.db.get_channel(channel_id)
        if not existing_config:
            return None, "not_found"
        
        # Create a merged config
        new_config = existing_config.copy()
        new_config.update(update_data)

        if not self._is_valid_config(new_config):
            return None, "bad_request" # Invalid resulting data
        
        updated_config = self.db.save_channel(channel_id, new_config)
        return updated_config, "success"

    def delete_channel(self, channel_id):
        """Deletes a channel."""
        if self.db.delete_channel(channel_id):
            return True, "success"
        return False, "not_found"

# 3. API Layer (api.py)
# Simulates a web API that the UI would interact with.

class APIHandler:
    """Simulates an API endpoint handler."""
    def __init__(self, manager):
        self.manager = manager

    def handle_request(self, method, channel_id, data=None):
        """A single entry point to simulate different HTTP methods."""
        if method == "GET":
            config = self.manager.get_channel_config(channel_id)
            if config:
                return 200, config
            else:
                return 404, {"error": "Channel not found"}

        elif method == "POST":
            config, status = self.manager.create_channel(channel_id, data)
            if status == "created":
                return 201, config
            elif status == "conflict":
                return 409, {"error": "Channel already exists"}
            else: # bad_request
                return 400, {"error": "Invalid configuration data"}

        elif method == "PUT":
            config, status = self.manager.update_channel_config(channel_id, data)
            if status == "success":
                return 200, config
            elif status == "not_found":
                return 404, {"error": "Channel not found"}
            else: # bad_request
                return 400, {"error": "Invalid configuration data"}

        elif method == "DELETE":
            success, status = self.manager.delete_channel(channel_id)
            if success:
                return 204, None
            else: # not_found
                return 404, {"error": "Channel not found"}
        
        return 405, {"error": "Method not allowed"}

# 4. UI Layer Mock (ui_mock.py)
# A mock class that simulates user actions on the configuration page.

class UIMock:
    """Simulates a user interacting with the Channel Configuration Page."""
    def __init__(self, api_handler):
        self.api = api_handler
        self.last_response_status = None
        self.last_response_data = None

    def _make_request(self, method, channel_id, data=None):
        self.last_response_status, self.last_response_data = self.api.handle_request(method, channel_id, data)

    def load_channel_form(self, channel_id):
        """Simulates loading an existing channel's data into the UI form."""
        self._make_request("GET", channel_id)
        return self.last_response_data

    def click_save_new_button(self, channel_id, form_data):
        """Simulates filling the form and clicking 'Save' for a new channel."""
        self._make_request("POST", channel_id, form_data)

    def click_update_button(self, channel_id, form_data):
        """Simulates editing the form and clicking 'Update' for an existing channel."""
        self._make_request("PUT", channel_id, form_data)

    def click_delete_button(self, channel_id):
        """Simulates clicking the 'Delete' button for a channel."""
        self._make_request("DELETE", channel_id)

# --- Integration Test ---

class TestChannelConfigIntegration(unittest.TestCase):

    def setUp(self):
        """
        Set up the full stack for each test.
        This ensures tests are isolated from each other.
        """
        # 1. Initialize the database (and clear it)
        self.db = ChannelDatabase()
        self.db.clear()

        # 2. Initialize the manager with the database
        self.manager = ConfigManager(self.db)

        # 3. Initialize the API with the manager
        self.api = APIHandler(self.manager)

        # 4. Initialize the UI mock with the API
        self.ui = UIMock(self.api)
        
        # Define some standard data for tests
        self.channel_id = "general"
        self.initial_data = {
            "name": "General Channel",
            "topic": "Company-wide announcements",
            "settings": {"is_private": False, "retention_days": 365}
        }
        self.update_data = {
            "topic": "All-hands meetings and announcements",
            "settings": {"is_private": False, "retention_days": 730}
        }

    def test_full_lifecycle_create_read_update_delete(self):
        """
        Tests the entire user flow: creating, loading, updating, and deleting a channel config.
        """
        # 1. CREATE: User creates a new channel configuration
        self.ui.click_save_new_button(self.channel_id, self.initial_data)
        
        # Assert UI receives correct API response
        self.assertEqual(self.ui.last_response_status, 201)
        self.assertEqual(self.ui.last_response_data, self.initial_data)
        
        # Assert database state directly
        db_state = self.db.get_channel(self.channel_id)
        self.assertIsNotNone(db_state)
        self.assertEqual(db_state["name"], "General Channel")

        # 2. READ: User navigates back to the page and loads the data
        loaded_data = self.ui.load_channel_form(self.channel_id)
        
        # Assert UI receives correct data and status
        self.assertEqual(self.ui.last_response_status, 200)
        self.assertEqual(loaded_data, self.initial_data)

        # 3. UPDATE: User changes the topic and retention policy
        self.ui.click_update_button(self.channel_id, self.update_data)
        
        # Assert UI receives correct API response
        self.assertEqual(self.ui.last_response_status, 200)
        self.assertEqual(self.ui.last_response_data["topic"], self.update_data["topic"])
        self.assertEqual(self.ui.last_response_data["settings"]["retention_days"], 730)

        # Assert database state directly after update
        db_state_after_update = self.db.get_channel(self.channel_id)
        self.assertEqual(db_state_after_update["topic"], "All-hands meetings and announcements")
        self.assertEqual(db_state_after_update["name"], "General Channel") # Name should be unchanged

        # 4. DELETE: User deletes the channel configuration
        self.ui.click_delete_button(self.channel_id)
        
        # Assert UI receives correct API response
        self.assertEqual(self.ui.last_response_status, 204)
        self.assertIsNone(self.ui.last_response_data)

        # 5. VERIFY DELETION: User tries to load the deleted channel
        self.ui.load_channel_form(self.channel_id)
        
        # Assert UI receives a 'Not Found' response
        self.assertEqual(self.ui.last_response_status, 404)

        # Assert database state is empty
        self.assertIsNone(self.db.get_channel(self.channel_id))

    def test_create_channel_with_invalid_data(self):
        """
        Tests that the system rejects creating a channel with missing required fields.
        """
        invalid_data = {
            "topic": "A channel with no name" # Missing 'name' field
        }
        self.ui.click_save_new_button("invalid-channel", invalid_data)

        # Assert UI gets a Bad Request error
        self.assertEqual(self.ui.last_response_status, 400)
        self.assertIn("error", self.ui.last_response_data)
        
        # Assert nothing was written to the database
        self.assertIsNone(self.db.get_channel("invalid-channel"))

    def test_create_existing_channel_fails(self):
        """
        Tests that the system prevents creating a channel that already exists.
        """
        # Create the channel first
        self.ui.click_save_new_button(self.channel_id, self.initial_data)
        self.assertEqual(self.ui.last_response_status, 201)

        # Attempt to create it again
        second_attempt_data = {"name": "Duplicate", "topic": "This should fail"}
        self.ui.click_save_new_button(self.channel_id, second_attempt_data)

        # Assert UI gets a Conflict error
        self.assertEqual(self.ui.last_response_status, 409)
        self.assertIn("error", self.ui.last_response_data)

        # Assert the original data in the database remains unchanged
        db_state = self.db.get_channel(self.channel_id)
        self.assertEqual(db_state, self.initial_data)

    def test_update_nonexistent_channel_fails(self):
        """
        Tests that updating a channel that doesn't exist results in an error.
        """
        self.ui.click_update_button("nonexistent-channel", self.update_data)

        # Assert UI gets a Not Found error
        self.assertEqual(self.ui.last_response_status, 404)
        self.assertIn("error", self.ui.last_response_data)

    def test_update_with_invalid_data_fails(self):
        """
        Tests that updating a channel with data that makes it invalid is rejected.
        """
        # First, create a valid channel
        self.ui.click_save_new_button(self.channel_id, self.initial_data)
        self.assertEqual(self.ui.last_response_status, 201)

        # Now, try to update it with an empty name, which is invalid
        invalid_update = {"name": "   "}
        self.ui.click_update_button(self.channel_id, invalid_update)

        # Assert UI gets a Bad Request error
        self.assertEqual(self.ui.last_response_status, 400)
        
        # Assert the database state has not changed from the original
        db_state = self.db.get_channel(self.channel_id)
        self.assertEqual(db_state, self.initial_data)

    def test_delete_nonexistent_channel_fails(self):
        """
        Tests that deleting a channel that doesn't exist results in an error.
        """
        self.ui.click_delete_button("nonexistent-channel")

        # Assert UI gets a Not Found error
        self.assertEqual(self.ui.last_response_status, 404)
        self.assertIn("error", self.ui.last_response_data)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)