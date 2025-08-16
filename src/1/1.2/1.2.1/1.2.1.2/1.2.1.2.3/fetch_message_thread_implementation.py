import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logging.basicConfig(level=logging.INFO)

def fetch_message_thread(client: WebClient, channel_id: str, thread_ts: str):
    """
    Fetches all messages from a specific Slack thread.

    This function uses the `conversations.replies` API method to retrieve
    the full conversation thread, including the initial parent message.

    Args:
        client (WebClient): An instance of the slack_sdk.WebClient,
                            initialized with a bot token.
        channel_id (str): The ID of the public or private channel containing the thread.
        thread_ts (str): The 'ts' (timestamp) of the parent message that
                         identifies the thread.

    Returns:
        list: A list of message dictionaries from the thread. The first message
              in the list is the parent message. Returns an empty list if
              the thread cannot be found or an API error occurs.
    """
    try:
        logging.info(f"Fetching thread with ts={thread_ts} from channel={channel_id}")
        result = client.conversations_replies(
            channel=channel_id,
            ts=thread_ts
        )
        messages = result.get("messages", [])
        if messages:
            logging.info(f"Successfully fetched {len(messages)} messages from the thread.")
        else:
            logging.warning(f"No messages found for thread {thread_ts} in channel {channel_id}.")
        return messages
    except SlackApiError as e:
        # Log the specific Slack API error
        logging.error(f"Error fetching Slack thread: {e.response['error']}")
        return []
    except Exception as e:
        # Log any other unexpected exceptions
        logging.error(f"An unexpected error occurred while fetching thread: {e}")
        return []