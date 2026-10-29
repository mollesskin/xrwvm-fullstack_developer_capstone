import os
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()

def _configured_url(primary, legacy, default):
    value = os.getenv(primary) or os.getenv(legacy) or default
    return (value if value.startswith(("http://", "https://")) else default).rstrip("/")


backend_url = _configured_url("BACKEND_URL", "backend_url", "http://localhost:3030")
sentiment_analyzer_url = _configured_url(
    "SENTIMENT_ANALYZER_URL", "sentiment_analyzer_url", "http://localhost:5050"
)


def get_request(endpoint):
    response = requests.get(f"{backend_url}/{endpoint.lstrip('/')}", timeout=10)
    response.raise_for_status()
    return response.json()


def analyze_review_sentiments(review_text):
    response = requests.get(
        f"{sentiment_analyzer_url}/analyze/{quote(review_text, safe='')}", timeout=10
    )
    response.raise_for_status()
    return response.json().get("sentiment", "neutral")


def post_review(data_dict):
    response = requests.post(f"{backend_url}/insert_review", json=data_dict, timeout=10)
    response.raise_for_status()
    return response.json()
