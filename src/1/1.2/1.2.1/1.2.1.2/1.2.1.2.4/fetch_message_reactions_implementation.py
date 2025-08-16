import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logging.basicConfig(level=logging.INFO)

def fetch_message_reactions(client: WebClient, channel_id: str, message_ts: str):
    """
    Fetches all reactions for a specific Slack message.

    This function uses the `reactions.get` API method to retrieve a list of
    reactions for a given message, identified by its channel and timestamp.

    Args:
        client (WebClient): An instance of the slack_sdk.WebClient,
                            initialized with a bot token.
        channel_id (str): The ID of the channel where the message was posted.
        message_ts (str): The 'ts' (timestamp) of the message to fetch reactions for.

    Returns:
        list: A list of reaction dictionaries. Each dictionary contains details
              like the reaction name, count, and the users who added it.
              Returns an empty list if the message has no reactions or if an
              API error occurs (e.g., message not found).
    """
    try:
        logging.info(f"Fetching reactions for message ts={message_ts} in channel={channel_id}")
        result = client.reactions_get(
            channel=channel_id,
            timestamp=message_ts
        )
        
        # The reactions list is nested inside the 'message' object
        message_details = result.get("message", {})
        reactions = message_details.get("reactions", [])

        if reactions:
            logging.info(f"Successfully fetched {len(reactions)} types of reactions for message {message_ts}.")
        else:
            logging.info(f"No reactions found for message {message_ts}.")
            
        return reactions

    except SlackApiError as e:
        # The 'message_not_found' error is common if the message has no reactions
        # or has been deleted. We can treat it as a non-fatal error.
        if e.response["error"] == "message_not_found":
            logging.warning(f"Message {message_ts} not found or has no reactions.")
        else:
            logging.error(f"Error fetching reactions from Slack API: {e.response['error']}")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred while fetching reactions: {e}")
        return []