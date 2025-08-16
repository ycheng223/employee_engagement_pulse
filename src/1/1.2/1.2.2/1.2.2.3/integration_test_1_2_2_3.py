import unittest

# Assume these functions would exist in separate modules and are imported.
# For this integration test, we'll define them here as stubs/mocks
# to simulate the data they would provide to the main combination function.

def mock_get_text_sentiment(message_text):
    """
    Mock function simulating a text sentiment analysis model.
    Returns a score from -1.0 to 1.0.
    """
    if "love" in message_text or "wonderful" in message_text:
        return 0.9
    if "hate" in message_text or "awful" in message_text:
        return -0.8
    if "sarcastic" in message_text: # A tricky case
        return 0.5
    if "neutral" in message_text:
        return 0.0
    return 0.1 # Default neutral-positive

def mock_get_thread_sentiment(thread_context):
    """
    Mock function simulating the analysis of a conversation's overall sentiment.
    Here, it just returns a pre-calculated value from a dictionary.
    """
    if thread_context == "positive_discussion":
        return 0.7
    if thread_context == "heated_argument":
        return -0.6
    if thread_context == "neutral_info_exchange":
        return 0.05
    return 0.0

def mock_get_reaction_sentiment(reactions):
    """
    Mock function simulating the conversion of user reactions/emojis into a sentiment score.
    """
    score = 0.0
    if not reactions:
        return 0.0
    for reaction in reactions:
        if reaction == 'like':
            score += 0.8
        elif reaction == 'love':
            score += 1.0
        elif reaction == 'angry':
            score -= 0.9
        elif reaction == 'laugh': # Can be ambiguous, treated as positive here
            score += 0.4
    return score / len(reactions) if reactions else 0.0


# The actual implementation to be tested, as provided in the context.
# In a real scenario, this would be `from sentiment_combiner import combine_sentiment_scores`.
def combine_sentiment_scores(
    text_sentiment,
    thread_sentiment,
    reaction_sentiment,
    text_weight=0.5,
    thread_weight=0.2,
    reaction_weight=0.3
):
    """
    Combines text, thread, and reaction sentiment scores using a weighted average.
    """
    if not abs((text_weight + thread_weight + reaction_weight) - 1.0) < 1e-9:
        raise ValueError("The sum of all weights must be equal to 1.0.")

    combined_score = (
        (text_sentiment * text_weight) +
        (thread_sentiment * thread_weight) +
        (reaction_sentiment * reaction_weight)
    )

    return combined_score


class TestCombinedMessageSentimentIntegration(unittest.TestCase):
    """
    Integration tests for the overall message sentiment scoring process.

    These tests simulate a full workflow:
    1. A message, its context, and its reactions are defined.
    2. Mocked analyzer functions generate individual sentiment scores for each component.
    3. The `combine_sentiment_scores` function is called with these scores.
    4. The final, combined score is verified.
    """

    def test_overwhelmingly_positive_message(self):
        """
        Scenario: A very positive message in a positive thread with positive reactions.
        The final score should be strongly positive.
        """
        # 1. Define inputs for the scenario
        message_text = "This is a wonderful update, I love it!"
        thread_context = "positive_discussion"
        reactions = ['love', 'like', 'like']

        # 2. Get scores from (mocked) individual analyzer components
        text_sentiment = mock_get_text_sentiment(message_text)       # Expected: 0.9
        thread_sentiment = mock_get_thread_sentiment(thread_context) # Expected: 0.7
        reaction_sentiment = mock_get_reaction_sentiment(reactions)  # Expected: (1.0 + 0.8 + 0.8) / 3 = 0.8667

        self.assertAlmostEqual(text_sentiment, 0.9)
        self.assertAlmostEqual(thread_sentiment, 0.7)
        self.assertAlmostEqual(reaction_sentiment, 0.8667, places=4)

        # 3. Call the integration target function
        final_score = combine_sentiment_scores(text_sentiment, thread_sentiment, reaction_sentiment)

        # 4. Verify the result
        # Expected: (0.9 * 0.5) + (0.7 * 0.2) + (0.8667 * 0.3)
        #         = 0.45 + 0.14 + 0.26001 = 0.85001
        expected_final_score = 0.850
        self.assertAlmostEqual(final_score, expected_final_score, places=3)

    def test_negative_message_in_heated_thread(self):
        """
        Scenario: A negative message in a negative thread with negative reactions.
        The final score should be strongly negative.
        """
        # 1. Define inputs
        message_text = "I hate this new feature, it's awful."
        thread_context = "heated_argument"
        reactions = ['angry', 'angry']

        # 2. Get scores from individual components
        text_sentiment = mock_get_text_sentiment(message_text)       # Expected: -0.8
        thread_sentiment = mock_get_thread_sentiment(thread_context) # Expected: -0.6
        reaction_sentiment = mock_get_reaction_sentiment(reactions)  # Expected: (-0.9 - 0.9) / 2 = -0.9

        # 3. Call the integration target
        final_score = combine_sentiment_scores(text_sentiment, thread_sentiment, reaction_sentiment)

        # 4. Verify
        # Expected: (-0.8 * 0.5) + (-0.6 * 0.2) + (-0.9 * 0.3)
        #         = -0.40 - 0.12 - 0.27 = -0.79
        expected_final_score = -0.79
        self.assertAlmostEqual(final_score, expected_final_score)

    def test_sarcastic_message_clarified_by_context(self):
        """
        Scenario: A text that appears positive is clarified as negative by
        the thread context and reactions.
        """
        # 1. Define inputs
        message_text = "Oh, this is just a sarcastic and wonderful change." # Text model sees this as positive
        thread_context = "heated_argument"
        reactions = ['angry']

        # 2. Get scores
        text_sentiment = mock_get_text_sentiment(message_text)       # Expected: 0.5 (tricked by "wonderful")
        thread_sentiment = mock_get_thread_sentiment(thread_context) # Expected: -0.6
        reaction_sentiment = mock_get_reaction_sentiment(reactions)  # Expected: -0.9

        self.assertAlmostEqual(text_sentiment, 0.5) # Verify the mock's tricky behavior

        # 3. Call the integration target
        final_score = combine_sentiment_scores(text_sentiment, thread_sentiment, reaction_sentiment)

        # 4. Verify - the negative context should pull the score down
        # Expected: (0.5 * 0.5) + (-0.6 * 0.2) + (-0.9 * 0.3)
        #         = 0.25 - 0.12 - 0.27 = -0.14
        expected_final_score = -0.14
        self.assertAlmostEqual(final_score, expected_final_score)
        self.assertTrue(final_score < 0, "Final score should be negative despite positive text score")

    def test_neutral_message_influenced_by_positive_reactions(self):
        """
        Scenario: A neutral message's sentiment is defined primarily by its positive context.
        """
        # 1. Define inputs
        message_text = "This is a neutral statement."
        thread_context = "positive_discussion"
        reactions = ['like', 'like', 'love']

        # 2. Get scores
        text_sentiment = mock_get_text_sentiment(message_text)       # Expected: 0.0
        thread_sentiment = mock_get_thread_sentiment(thread_context) # Expected: 0.7
        reaction_sentiment = mock_get_reaction_sentiment(reactions)  # Expected: (0.8 + 0.8 + 1.0) / 3 = 0.8667

        # 3. Call the integration target
        final_score = combine_sentiment_scores(text_sentiment, thread_sentiment, reaction_sentiment)

        # 4. Verify
        # Expected: (0.0 * 0.5) + (0.7 * 0.2) + (0.8667 * 0.3)
        #         = 0.0 + 0.14 + 0.26001 = 0.40001
        expected_final_score = 0.400
        self.assertAlmostEqual(final_score, expected_final_score, places=3)
        self.assertTrue(final_score > 0.3, "Final score should be clearly positive due to context")

    def test_integration_with_reaction_focused_weights(self):
        """
        Scenario: A system prioritizes user reactions over text.
        A positive text in a negative thread should be swayed by positive reactions.
        """
        # 1. Define inputs
        message_text = "This is a wonderful update, I love it!"
        thread_context = "heated_argument" # Negative context
        reactions = ['love', 'love', 'love', 'love'] # Overwhelmingly positive reactions

        # 2. Get scores
        text_sentiment = mock_get_text_sentiment(message_text)       # Expected: 0.9
        thread_sentiment = mock_get_thread_sentiment(thread_context) # Expected: -0.6
        reaction_sentiment = mock_get_reaction_sentiment(reactions)  # Expected: 1.0

        # 3. Call the integration target with custom weights
        final_score = combine_sentiment_scores(
            text_sentiment,
            thread_sentiment,
            reaction_sentiment,
            text_weight=0.1,      # Low weight for text
            thread_weight=0.1,    # Low weight for thread
            reaction_weight=0.8   # High weight for reactions
        )

        # 4. Verify
        # Expected: (0.9 * 0.1) + (-0.6 * 0.1) + (1.0 * 0.8)
        #         = 0.09 - 0.06 + 0.80 = 0.83
        expected_final_score = 0.83
        self.assertAlmostEqual(final_score, expected_final_score)
        self.assertTrue(final_score > 0.8, "Final score should be very high due to reaction weight")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)