from textblob import TextBlob


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