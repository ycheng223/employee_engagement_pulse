import unittest
import logging
import json
import io
import sys
from datetime import datetime

# Implementation for 1.4.3/1.4.3.1
class JsonFormatter(logging.Formatter):
    """
    Custom log formatter that outputs log records as JSON strings.
    """
    def format(self, record):
        """
        Formats a log record into a JSON object.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The JSON formatted log string.
        """
        log_object = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name
        }
        if record.exc_info:
            log_object['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(log_object)


class DeploymentOperationsIntegrationTest(unittest.TestCase):
    """
    Integration test for the Deployment & Operations task, specifically
    testing the JsonFormatter's integration with the standard logging library.
    """

    def setUp(self):
        """
        Set up a logger with the custom JsonFormatter for each test.
        The log output is captured in an in-memory stream (io.StringIO).
        """
        self.logger = logging.getLogger(f'integration_test_{self.id()}')
        self.logger.setLevel(logging.DEBUG)

        # To prevent logs from propagating to the root logger and appearing in the console
        self.logger.propagate = False

        # Use an in-memory stream to capture the formatted log output
        self.stream = io.StringIO()
        self.handler = logging.StreamHandler(self.stream)

        # Instantiate and set the custom formatter
        formatter = JsonFormatter()
        self.handler.setFormatter(formatter)

        # Clear any existing handlers and add our new one
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        self.logger.addHandler(self.handler)

    def tearDown(self):
        """
        Clean up by removing the handler and closing the stream.
        """
        self.logger.removeHandler(self.handler)
        self.handler.close()

    def _get_json_log_output(self):
        """
        Helper method to retrieve, strip, and parse the JSON log
        output from the in-memory stream.
        """
        self.stream.seek(0)
        output = self.stream.getvalue().strip()
        self.assertTrue(output, "Log output was empty")
        return json.loads(output)

    def test_standard_log_message_format(self):
        """
        Tests if a standard INFO log message is correctly formatted into JSON.
        Verifies all expected fields (timestamp, level, message, name) are present
        and have the correct values and types.
        """
        log_message = "User successfully logged in."
        self.logger.info(log_message)

        log_output = self._get_json_log_output()

        self.assertEqual(log_output.get("level"), "INFO")
        self.assertEqual(log_output.get("message"), log_message)
        self.assertTrue(log_output.get("name").startswith('integration_test_'))
        self.assertIn("timestamp", log_output)
        
        # Verify timestamp is a valid ISO 8601 format string ending with 'Z'
        timestamp_str = log_output.get("timestamp")
        self.assertIsInstance(timestamp_str, str)
        self.assertTrue(timestamp_str.endswith("Z"))
        try:
            # Test if the timestamp can be parsed
            datetime.fromisoformat(timestamp_str[:-1])
        except ValueError:
            self.fail(f"Timestamp '{timestamp_str}' is not a valid ISO 8601 format.")

    def test_log_with_exception_info(self):
        """
        Tests if a log message with exception information includes the 'exc_info'
        field containing the formatted traceback. This tests the conditional
        logic within the formatter.
        """
        error_message = "Failed to process user request due to an error."
        try:
            raise ValueError("Invalid user ID")
        except ValueError:
            # exc_info=True captures the exception information
            self.logger.error(error_message, exc_info=True)

        log_output = self._get_json_log_output()

        self.assertEqual(log_output.get("level"), "ERROR")
        self.assertEqual(log_output.get("message"), error_message)
        self.assertIn("exc_info", log_output)

        exc_info_str = log_output.get("exc_info")
        self.assertIsInstance(exc_info_str, str)
        # Check for key phrases in a standard Python traceback
        self.assertIn("Traceback (most recent call last):", exc_info_str)
        self.assertIn('raise ValueError("Invalid user ID")', exc_info_str)
        self.assertIn("ValueError: Invalid user ID", exc_info_str)

    def test_log_without_exception_info(self):
        """
        Tests if a standard log message (without an exception) correctly omits
        the 'exc_info' field.
        """
        log_message = "System shutdown initiated."
        self.logger.critical(log_message)

        log_output = self._get_json_log_output()

        self.assertEqual(log_output.get("level"), "CRITICAL")
        self.assertNotIn("exc_info", log_output)

    def test_different_log_levels(self):
        """
        Tests that various log levels are correctly represented as strings
        in the final JSON output.
        """
        test_cases = {
            logging.DEBUG: ("Fetching data from database.", "DEBUG"),
            logging.WARNING: ("API response time is high.", "WARNING"),
        }

        for level, (message, expected_level_str) in test_cases.items():
            # Reset stream for each log message
            self.stream.seek(0)
            self.stream.truncate(0)

            self.logger.log(level, message)
            log_output = self._get_json_log_output()

            self.assertEqual(log_output.get("level"), expected_level_str)
            self.assertEqual(log_output.get("message"), message)


if __name__ == '__main__':
    unittest.main()