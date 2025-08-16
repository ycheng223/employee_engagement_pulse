import unittest
from textblob import TextBlob


# The implementation to be tested is assumed to be in the same file or imported.
def analyze_text(text: str, *, analyses: list[str] | None = None, **options: any) -> dict[str, any]:
    """
    Analyzes the given text for various properties, including sentiment.

    Args:
        text: The input string to analyze.
        analyses: A list of specific analyses to perform. If None, performs
                  all available analyses. Currently, only 'sentiment' is
                  supported.
        **options: Additional options for the analysis (currently unused).

    Returns:
        A dictionary where keys are the names of the analyses and values
        are the results of those analyses. For 'sentiment', the result is
        a dictionary with 'polarity' and 'subjectivity'.
    """
    results: dict[str, any] = {}

    # Determine if sentiment analysis should be performed.
    # It runs if `analyses` is not specified (None) or if 'sentiment' is in the list.
    should_run_sentiment = analyses is None or 'sentiment' in analyses

    if should_run_sentiment:
        # Perform sentiment analysis using TextBlob
        blob = TextBlob(text)
        sentiment_data = blob.sentiment

        # Structure the sentiment result
        results['sentiment'] = {
            'polarity': sentiment_data.polarity,
            'subjectivity': sentiment_data.subjectivity
        }

    # This structure allows for easy extension with other analyses in the future.
    # For example:
    # if analyses is None or 'word_counts' in analyses:
    #     results['word_counts'] = blob.word_counts

    return results


class TestAnalyzeText(unittest.TestCase):

    def test_positive_sentiment(self):
        """Tests analysis of a text with clearly positive sentiment."""
        text = "This is a wonderful and fantastic product. I am very happy!"
        result = analyze_text(text)
        self.assertIn('sentiment', result)
        self.assertIsInstance(result['sentiment'], dict)
        self.assertIn('polarity', result['sentiment'])
        self.assertIn('subjectivity', result['sentiment'])
        self.assertGreater(result['sentiment']['polarity'], 0.5)
        self.assertGreater(result['sentiment']['subjectivity'], 0.5)

    def test_negative_sentiment(self):
        """Tests analysis of a text with clearly negative sentiment."""
        text = "I had a terrible and awful experience. It was very bad."
        result = analyze_text(text)
        self.assertIn('sentiment', result)
        polarity = result['sentiment']['polarity']
        subjectivity = result['sentiment']['subjectivity']
        self.assertLess(polarity, -0.5)
        self.assertGreater(subjectivity, 0.5)

    def test_neutral_sentiment(self):
        """Tests analysis of a text with neutral sentiment."""
        text = "The sky is typically blue."
        result = analyze_text(text)
        self.assertIn('sentiment', result)
        # Neutral text should have a polarity at or very close to 0.
        self.assertAlmostEqual(result['sentiment']['polarity'], 0.0, places=1)
        # Factual statements should have low subjectivity.
        self.assertLess(result['sentiment']['subjectivity'], 0.5)
        
    def test_empty_string_input(self):
        """Tests the function with an empty string."""
        text = ""
        result = analyze_text(text)
        self.assertIn('sentiment', result)
        self.assertEqual(result['sentiment']['polarity'], 0.0)
        self.assertEqual(result['sentiment']['subjectivity'], 0.0)

    def test_analysis_explicitly_requested(self):
        """Tests that analysis runs when 'sentiment' is in the analyses list."""
        text = "This is a great test."
        result = analyze_text(text, analyses=['sentiment'])
        self.assertIn('sentiment', result)
        self.assertGreater(result['sentiment']['polarity'], 0)

    def test_analysis_not_requested(self):
        """Tests that analysis does not run if 'sentiment' is not in the list."""
        text = "This text should not be analyzed."
        result = analyze_text(text, analyses=['word_count'])
        self.assertEqual(result, {})

    def test_empty_analyses_list(self):
        """Tests that analysis does not run for an empty analyses list."""
        text = "This text should also not be analyzed."
        result = analyze_text(text, analyses=[])
        self.assertEqual(result, {})

    def test_unused_options_are_ignored(self):
        """Tests that additional keyword arguments do not affect the result."""
        text = "This is a simple test."
        # The function should ignore the 'strict' and 'language' options.
        result = analyze_text(text, strict=True, language='en')
        self.assertIn('sentiment', result)
        self.assertIn('polarity', result['sentiment'])