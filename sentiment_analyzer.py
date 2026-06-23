from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    """
    Analyze sentiment of text using VADER
    Returns dict with sentiment label and scores
    """
    if not text or len(text.strip()) < 3:
        return {
            'label': 'Neutral',
            'pos': 0,
            'neg': 0,
            'neu': 1.0,
            'compound': 0
        }

    scores = analyzer.polarity_scores(text)

    if scores['compound'] >= 0.05:
        label = 'Positive'
    elif scores['compound'] <= -0.05:
        label = 'Negative'
    else:
        label = 'Neutral'

    return {
        'label': label,
        'pos': round(scores['pos'], 3),
        'neg': round(scores['neg'], 3),
        'neu': round(scores['neu'], 3),
        'compound': round(scores['compound'], 3)
    }
