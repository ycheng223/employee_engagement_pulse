import unittest
from unittest.mock import MagicMock, patch
from slack_sdk.errors import SlackApiError

# Assuming the function is in a file named 'data_ingestion_service.py'
from data_ingestion_service import fetch_message_thread

class TestFetchMessageThread(unittest.TestCase):
    """
    Unit tests for the fetch_message_thread function.
    """

    def setUp(self):
        """
        Set up a mock WebClient and test data for each test.
        """
        self.mock_client = MagicMock()
        self.channel_id = "C123ABC456"
        self.thread_ts = "1678886400.123456"

    @patch('data_ingestion_service.logging')
    def test_successful_fetch_returns_messages(self, mock_logging):
        """
        Tests that the function returns a list of messages on a successful API call.
        """
        # Arrange
        expected_messages = [
            {"ts": self.thread_ts, "text": "This is the parent message."},
            {"ts": "1678886405.654321", "text": "This is a reply."}
        ]
        api_response = {"ok": True, "messages": expected_messages}
        self.mock_client.conversations_replies.return_value = api_response

        # Act
        result = fetch_message_thread(self.mock_client, self.channel_id, self.thread_ts)

        # Assert
        self.mock_client.conversations_replies.assert_called_once_with(
            channel=self.channel_id,
            ts=self.thread_ts
        )
        self.assertEqual(result, expected_messages)
        mock_logging.info.assert_any_call(f"Fetching thread with ts={self.thread_ts} from channel={self.channel_id}")
        mock_logging.info.assert_any_call(f"Successfully fetched {len(expected_messages)} messages from the thread.")
        mock_logging.error.assert_not_called()

    @patch('data_ingestion_service.logging')
    def test_no_messages_found_returns_empty_list(self, mock_logging):
        """
        Tests that the function returns an empty list and logs a warning when the API response has no messages.
        """
        # Arrange
        api_response = {"ok": True, "messages": []}
        self.mock_client.conversations_replies.return_value = api_response

        # Act
        result = fetch_message_thread(self.mock_client, self.channel_id, self.thread_ts)

        # Assert
        self.mock_client.conversations_replies.assert_called_once_with(
            channel=self.channel_id,
            ts=self.thread_ts
        )
        self.assertEqual(result, [])
        mock_logging.warning.assert_called_once_with(
            f"No messages found for thread {self.thread_ts} in channel {self.channel_id}."
        )

    @patch('data_ingestion_service.logging')
    def test_slack_api_error_returns_empty_list(self, mock_logging):
        """
        Tests that the function catches a SlackApiError, logs it, and returns an empty list.
        """
        # Arrange
        error_response = {"ok": False, "error": "channel_not_found"}
        slack_error = SlackApiError(message="Channel not found", response=error_response)
        self.mock_client.conversations_replies.side_effect = slack_error

        # Act
        result = fetch_message_thread(self.mock_client, self.channel_id, self.thread_ts)

        # Assert
        self.assertEqual(result, [])
        mock_logging.error.assert_called_once_with(
            f"Error fetching Slack thread: {error_response['error']}"
        )
        mock_logging.info.assert_called_once_with(f"Fetching thread with ts={self.thread_ts} from channel={self.channel_id}")

    @patch('data_ingestion_service.logging')
    def test_unexpected_exception_returns_empty_list(self, mock_logging):
        """
        Tests that the function catches a generic Exception, logs it, and returns an empty list.
        """
        # Arrange
        error_message = "A network error occurred"
        self.mock_client.conversations_replies.side_effect = Exception(error_message)

        # Act
        result = fetch_message_thread(self.mock_client, self.channel_id, self.thread_ts)

        # Assert
        self.assertEqual(result, [])
        mock_logging.error.assert_called_once_with(
            f"An unexpected error occurred while fetching thread: {error_message}"
        )
        mock_logging.info.assert_called_once_with(f"Fetching thread with ts={self.thread_ts} from channel={self.channel_id}")


if __name__ == '__main__':
    unittest.main()