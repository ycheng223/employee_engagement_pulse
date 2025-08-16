import unittest
from unittest.mock import MagicMock, patch
from slack_sdk.errors import SlackApiError

# Assuming the function is in a file named 'data_ingestion_service.py'
from data_ingestion_service import fetch_message_reactions

class TestFetchMessageReactions(unittest.TestCase):
    """
    Unit tests for the fetch_message_reactions function.
    """

    def setUp(self):
        """
        Set up a mock WebClient and test data for each test.
        """
        self.mock_client = MagicMock()
        self.channel_id = "C123ABC456"
        self.message_ts = "1678886400.123456"

    @patch('data_ingestion_service.logging')
    def test_successful_fetch_with_reactions(self, mock_logging):
        """
        Tests that the function returns a list of reactions on a successful API call.
        """
        # Arrange
        expected_reactions = [
            {"name": "thumbsup", "users": ["U123", "U456"], "count": 2},
            {"name": "heart", "users": ["U789"], "count": 1}
        ]
        api_response = {
            "ok": True,
            "message": {
                "text": "Hello world",
                "reactions": expected_reactions
            }
        }
        self.mock_client.reactions_get.return_value = api_response

        # Act
        result = fetch_message_reactions(self.mock_client, self.channel_id, self.message_ts)

        # Assert
        self.mock_client.reactions_get.assert_called_once_with(
            channel=self.channel_id,
            timestamp=self.message_ts
        )
        self.assertEqual(result, expected_reactions)
        mock_logging.info.assert_any_call(f"Fetching reactions for message ts={self.message_ts} in channel={self.channel_id}")
        mock_logging.info.assert_any_call(f"Successfully fetched {len(expected_reactions)} types of reactions for message {self.message_ts}.")

    @patch('data_ingestion_service.logging')
    def test_no_reactions_found_returns_empty_list(self, mock_logging):
        """
        Tests that the function returns an empty list when the message has no reactions.
        """
        # Arrange
        api_response = {
            "ok": True,
            "message": {
                "text": "Hello world",
                "reactions": []
            }
        }
        self.mock_client.reactions_get.return_value = api_response

        # Act
        result = fetch_message_reactions(self.mock_client, self.channel_id, self.message_ts)

        # Assert
        self.assertEqual(result, [])
        mock_logging.info.assert_any_call(f"Fetching reactions for message ts={self.message_ts} in channel={self.channel_id}")
        mock_logging.info.assert_any_call(f"No reactions found for message {self.message_ts}.")
        mock_logging.warning.assert_not_called()
        mock_logging.error.assert_not_called()

    @patch('data_ingestion_service.logging')
    def test_slack_api_error_message_not_found(self, mock_logging):
        """
        Tests that a 'message_not_found' API error is handled as a warning and returns an empty list.
        """
        # Arrange
        error_response = {"ok": False, "error": "message_not_found"}
        slack_error = SlackApiError(message="Message not found", response=error_response)
        self.mock_client.reactions_get.side_effect = slack_error

        # Act
        result = fetch_message_reactions(self.mock_client, self.channel_id, self.message_ts)

        # Assert
        self.assertEqual(result, [])
        mock_logging.warning.assert_called_once_with(f"Message {self.message_ts} not found or has no reactions.")
        mock_logging.error.assert_not_called()

    @patch('data_ingestion_service.logging')
    def test_other_slack_api_error(self, mock_logging):
        """
        Tests that other SlackApiErrors are logged as errors and return an empty list.
        """
        # Arrange
        error_response = {"ok": False, "error": "channel_not_found"}
        slack_error = SlackApiError(message="Channel not found", response=error_response)
        self.mock_client.reactions_get.side_effect = slack_error

        # Act
        result = fetch_message_reactions(self.mock_client, self.channel_id, self.message_ts)

        # Assert
        self.assertEqual(result, [])
        mock_logging.error.assert_called_once_with(f"Error fetching reactions from Slack API: {error_response['error']}")
        mock_logging.warning.assert_not_called()

    @patch('data_ingestion_service.logging')
    def test_unexpected_exception(self, mock_logging):
        """
        Tests that a generic Exception is caught, logged as an error, and returns an empty list.
        """
        # Arrange
        error_message = "A network error occurred"
        self.mock_client.reactions_get.side_effect = Exception(error_message)

        # Act
        result = fetch_message_reactions(self.mock_client, self.channel_id, self.message_ts)

        # Assert
        self.assertEqual(result, [])
        mock_logging.error.assert_called_once_with(
            f"An unexpected error occurred while fetching reactions: {error_message}"
        )

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)