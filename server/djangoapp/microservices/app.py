from flask import Flask
from nltk.sentiment import SentimentIntensityAnalyzer
from pathlib import Path
import nltk
import json
app = Flask("Sentiment Analyzer")

nltk.data.path.insert(0, str(Path(__file__).resolve().parent))
sia = SentimentIntensityAnalyzer()


@app.get('/')
def home():
    return "Welcome to the Sentiment Analyzer. \
    Use /analyze/text to get the sentiment"


@app.get('/analyze/<input_txt>')
def analyze_sentiment(input_txt):

    scores = sia.polarity_scores(input_txt)
    print(scores)
    compound = scores['compound']
    res = "positive" if compound >= 0.05 else "negative" if compound <= -0.05 else "neutral"
    res = json.dumps({"sentiment": res})
    print(res)
    return res


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
