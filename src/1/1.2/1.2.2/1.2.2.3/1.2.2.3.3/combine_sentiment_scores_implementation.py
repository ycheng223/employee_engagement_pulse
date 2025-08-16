import unittest

# The function to be tested, usually imported from another file.
# For example: from sentiment_combiner import combine_sentiment_scores
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

    This function calculates a single, unified sentiment score by taking into account
    the sentiment of the content itself, the conversational context (thread), and
    explicit user feedback (reactions). Each component is assigned a weight to
    determine its influence on the final score.

    Args:
        text_sentiment (float): The sentiment score of the primary text,
                                typically from -1.0 (very negative) to 1.0 (very positive).
        thread_sentiment (float): The average sentiment score of the surrounding
                                  thread or conversation.
        reaction_sentiment (float): A sentiment score derived from user reactions
                                    (e.g., likes, dislikes, emojis).
        text_weight (float, optional): The weight assigned to the text_sentiment.
                                       Defaults to 0.5.
        thread_weight (float, optional): The weight assigned to the thread_sentiment.
                                         Defaults to 0.2.
        reaction_weight (float, optional): The weight assigned to the reaction_sentiment.
                                           Defaults to 0.3.

    Returns:
        float: The final combined sentiment score.
    """
    # Using 'not == 1.0' can be problematic with floating-point numbers.
    # A tolerance check like 'abs(sum - 1.0) > 1e-9' would be more robust.
    # However, we test the function as it is written.
    if not (text_weight + thread_weight + reaction_weight) == 1.0:
        raise ValueError("The sum of all weights must be equal to 1.0.")

    combined_score = (
        (text_sentiment * text_weight) +
        (thread_sentiment * thread_weight) +
        (reaction_sentiment * reaction_weight)
    )

    return combined_score


class TestCombineSentimentScores(unittest.TestCase):
    """Unit tests for the combine_sentiment_scores function."""

    def test_all_positive_sentiments_default_weights(self):
        """Test combination of all positive sentiment scores with default weights."""
        text_sentiment = 0.8
        thread_sentiment = 0.6
        reaction_sentiment = 0.9
        # Expected: (0.8 * 0.5) + (0.6 * 0.2) + (0.9 * 0.3) = 0.4 + 0.12 + 0.27 = 0.79
        expected_score = 0.79
        result = combine_sentiment_scores(text_sentiment, thread_sentiment, reaction_sentiment)
        self.assertAlmostEqual(result, expected_score)

    def test_all_negative_sentiments_default_weights(self):
        """Test combination of all negative sentiment scores with default weights."""
        text_sentiment = -0.7
        thread_sentiment = -0.5
        reaction_sentiment = -0.2
        # Expected: (-0.7 * 0.5) + (-0.5 * 0.2) + (-0.2 * 0.3) = -0.35 - 0.10 - 0.06 = -0.51
        expected_score = -0.51
        result = combine_sentiment_scores(text_sentiment, thread_sentiment, reaction_sentiment)
        self.assertAlmostEqual(result, expected_score)

    def test_mixed_sentiments_default_weights(self):
        """Test combination of mixed sentiment scores with default weights."""
        text_sentiment = 0.9
        thread_sentiment = -0.4
        reaction_sentiment = 0.1
        # Expected: (0.9 * 0.5) + (-0.4 * 0.2) + (0.1 * 0.3) = 0.45 - 0.08 + 0.03 = 0.40
        expected_score = 0.40
        result = combine_sentiment_scores(text_sentiment, thread_sentiment, reaction_sentiment)
        self.assertAlmostEqual(result, expected_score)

    def test_all_neutral_sentiments(self):
        """Test combination of all neutral (zero) sentiment scores."""
        result = combine_sentiment_scores(0.0, 0.0, 0.0)
        self.assertEqual(result, 0.0)

    def test_boundary_values_sentiments(self):
        """Test combination of sentiment scores at the boundaries (-1.0 and 1.0)."""
        # Expected: (1.0 * 0.5) + (-1.0 * 0.2) + (1.0 * 0.3) = 0.5 - 0.2 + 0.3 = 0.6
        expected_score = 0.6
        result = combine_sentiment_scores(1.0, -1.0, 1.0)
        self.assertAlmostEqual(result, expected_score)

    def test_custom_weights(self):
        """Test the function with custom weights that sum to 1.0."""
        # Expected: (0.5 * 0.1) + (0.5 * 0.1) + (0.5 * 0.8) = 0.05 + 0.05 + 0.4 = 0.5
        expected_score = 0.5
        result = combine_sentiment_scores(
            text_sentiment=0.5,
            thread_sentiment=0.5,
            reaction_sentiment=0.5,
            text_weight=0.1,
            thread_weight=0.1,
            reaction_weight=0.8
        )
        self.assertAlmostEqual(result, expected_score)

    def test_invalid_weights_raise_value_error(self):
        """Test that a ValueError is raised if weights do not sum to 1.0."""
        with self.assertRaises(ValueError) as context:
            combine_sentiment_scores(
                text_sentiment=0.5,
                thread_sentiment=0.5,
                reaction_sentiment=0.5,
                text_weight=0.5,
                thread_weight=0.3, # Sum is 1.1
                reaction_weight=0.3
            )
        self.assertEqual(str(context.exception), "The sum of all weights must be equal to 1.0.")

    def test_weights_summing_less_than_one(self):
        """Test that a ValueError is raised if weights sum to less than 1.0."""
        with self.assertRaises(ValueError):
             combine_sentiment_scores(
                text_sentiment=0.5,
                thread_sentiment=0.5,
                reaction_sentiment=0.5,
                text_weight=0.4,
                thread_weight=0.2, # Sum is 0.9
                reaction_weight=0.3
            )

if __name__ == '__main__':
    unittest.main()