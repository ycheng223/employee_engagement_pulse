import unittest
from unittest.mock import patch, MagicMock, ANY

# Assuming the function is in a file named 'data_ingestion_service.py'
from data_ingestion_service import run_slack_events_listener

class TestSlackEventsListener(unittest.TestCase):
    """
    Unit tests for the run_slack_events_listener function.
    """

    @patch('data_ingestion_service.App')
    @patch('data_ingestion_service.logging')
    @patch.dict('data_ingestion_service.os.environ', {
        "SLACK_BOT_TOKEN": "test-bot-token",
        "SLACK_SIGNING_SECRET": "test-signing-secret"
    }, clear=True)
    def test_successful_startup_and_event_handling(self, mock_logging, MockApp):
        """
        Tests successful initialization, app start, and the logic of the message handler.
        """
        # Arrange: Mock the App instance and the decorator it returns
        mock_app_instance = MagicMock()
        mock_decorator = MagicMock()
        mock_app_instance.event.return_value = mock_decorator
        MockApp.return_value = mock_app_instance

        # Act: Run the main function
        run_slack_events_listener()

        # Assert: Check that the App was initialized correctly
        MockApp.assert_called_once_with(
            token="test-bot-token",
            signing_secret="test-signing-secret"
        )

        # Assert: Check that the event handler was registered for "message"
        mock_app_instance.event.assert_called_once_with("message")

        # Assert: Check that the app was started with the default port
        mock_logging.info.assert_any_call("Starting Slack Bolt app on port 3000")
        mock_app_instance.start.assert_called_once_with(port=3000)

        # --- Test the captured event handler function ---

        # Arrange: Capture the handler function that was passed to the decorator
        self.assertEqual(mock_decorator.call_count, 1)
        handler_function = mock_decorator.call_args.args[0]
        self.assertTrue(callable(handler_function))

        mock_handler_logger = MagicMock()

        # Case 1: A valid user message
        valid_body = {
            "event": {
                "type": "message",
                "user": "U12345",
                "text": "Hello world",
                "channel": "C67890",
            }
        }
        handler_function(body=valid_body, logger=mock_handler_logger)
        mock_handler_logger.info.assert_called_once_with(
            "Received message from user U12345 in channel C67890: 'Hello world'"
        )
        mock_handler_logger.reset_mock()

        # Case 2: A message with a subtype (e.g., channel join) should be ignored
        subtype_body = {
            "event": {
                "type": "message",
                "subtype": "channel_join",
                "user": "U12345",
                "text": "User has joined the channel",
            }
        }
        handler_function(body=subtype_body, logger=mock_handler_logger)
        mock_handler_logger.info.assert_not_called()
        mock_handler_logger.reset_mock()

        # Case 3: A message from a bot should be ignored
        bot_body = {
            "event": {
                "type": "message",
                "bot_id": "BABCDEF",
                "text": "This is a bot message",
            }
        }
        handler_function(body=bot_body, logger=mock_handler_logger)
        mock_handler_logger.info.assert_not_called()

    @patch('data_ingestion_service.App')
    @patch('data_ingestion_service.logging')
    @patch.dict('data_ingestion_service.os.environ', {}, clear=True)
    def test_missing_environment_variables(self, mock_logging, MockApp):
        """
        Tests that the function exits gracefully and logs an error if env vars are missing.
        """
        # Act
        run_slack_events_listener()

        # Assert
        mock_logging.error.assert_called_once_with(
            "Error: Environment variable 'SLACK_BOT_TOKEN' not set. Please set SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET."
        )
        MockApp.assert_not_called()

    @patch('data_ingestion_service.App')
    @patch('data_ingestion_service.logging')
    @patch.dict('data_ingestion_service.os.environ', {
        "SLACK_BOT_TOKEN": "test-bot-token",
        "SLACK_SIGNING_SECRET": "test-signing-secret"
    }, clear=True)
    def test_app_start_failure(self, mock_logging, MockApp):
        """
        Tests that an exception during app.start() is caught and logged.
        """
        # Arrange
        mock_app_instance = MagicMock()
        mock_app_instance.start.side_effect = Exception("Could not bind to port")
        MockApp.return_value = mock_app_instance

        # Act
        run_slack_events_listener()

        # Assert
        mock_app_instance.start.assert_called_once()
        mock_logging.error.assert_called_once_with("Failed to start the Slack app: Could not bind to port")

    @patch('data_ingestion_service.App')
    @patch('data_ingestion_service.logging')
    @patch.dict('data_ingestion_service.os.environ', {
        "SLACK_BOT_TOKEN": "test-bot-token",
        "SLACK_SIGNING_SECRET": "test-signing-secret",
        "PORT": "5000"
    }, clear=True)
    def test_custom_port_from_environment(self, mock_logging, MockApp):
        """
        Tests that the listener uses the PORT environment variable if it is set.
        """
        # Arrange
        mock_app_instance = MagicMock()
        MockApp.return_value = mock_app_instance

        # Act
        run_slack_events_listener()

        # Assert
        mock_logging.info.assert_any_call("Starting Slack Bolt app on port 5000")
        mock_app_instance.start.assert_called_once_with(port=5000)


if __name__ == '__main__':
    unittest.main()