# news_agent/app.py

import os
import time
import random
import requests
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

from config import NEWS_API_KEY, STRATEGY_AGENT_EVENT_URL
from a2a_client import send_event

app = Flask(__name__)

# For demonstration, list of sample “news” sources
NEWS_ENDPOINT = "https://newsapi.org/v2/top-headlines"

def fetch_news():
    """
    Fetches latest headlines (stub: random dummy data or use real NewsAPI).
    For real: 
        resp = requests.get(NEWS_ENDPOINT, params={
            "apiKey": NEWS_API_KEY,
            "q": "AAPL OR MSFT OR GOOG",
            "pageSize": 5
        })
        data = resp.json().get("articles", [])
    Here, we stub with random “sentiment score.”
    """
    # Real implementation (commented out):
    # resp = requests.get(NEWS_ENDPOINT, params={
    #     "apiKey": NEWS_API_KEY,
    #     "q": "AAPL OR MSFT OR GOOG",
    #     "pageSize": 5
    # })
    # articles = resp.json().get("articles", [])
    # sentiments = []
    # for art in articles:
    #     # Perform sentiment analysis or use a service
    #     sentiments.append(random.uniform(-1, 1))
    # avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

    # Stubbed random sentiment
    avg_sentiment = random.uniform(-1, 1)
    return avg_sentiment

def check_news():
    """
    Scheduled job (hourly):
      - Fetch average sentiment.
      - If |sentiment| >= 0.7, send news_alert to Strategy Agent.
    """
    sentiment = fetch_news()
    print(f"[NewsAgent] Avg sentiment: {sentiment:.2f}")

    if abs(sentiment) >= 0.7:
        alert_type = "positive" if sentiment > 0 else "negative"
        send_event(
            STRATEGY_AGENT_EVENT_URL,
            "news_alert",
            {"sentiment": sentiment, "alert": alert_type}
        )
        print(f"[NewsAgent] Sent news_alert: {alert_type}")

@app.route("/events", methods=["POST"])
def receive_event():
    """
    News Agent does not expect incoming events in this MVP.
    """
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_news, "interval", hours=1, next_run_time=time.time() + 1)
    scheduler.start()
    print("[NewsAgent] Scheduler started. Listening on port 5003.")
    app.run(host="0.0.0.0", port=5003)
