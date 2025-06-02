# fundamentals_agent/app.py

import os
import time
import random
import requests
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

from config import STRATEGY_AGENT_EVENT_URL
from a2a_client import send_event

app = Flask(__name__)

def fetch_fundamentals(symbol: str):
    """
    Stub: In reality, call a financial API to fetch balance sheet/income statement.
    E.g., AlphaVantage, FinancialModelingPrep.
    Here, we return random “cash ratio” data.
    """
    # Fake: cash ratio between 0.1 and 2.0
    return {"cash_ratio": random.uniform(0.1, 2.0)}

# Store last cash_ratio to detect anomaly
LAST_CASH_RATIO = {}

def check_fundamentals():
    """
    Scheduled job (once every 24h):
      - For each ticker, fetch fundamentals.
      - If cash ratio dropped more than 20% since last check, send alert.
    """
    tickers = ["AAPL", "MSFT", "GOOG"]
    for symbol in tickers:
        data = fetch_fundamentals(symbol)
        cash_ratio = data["cash_ratio"]
        prev = LAST_CASH_RATIO.get(symbol)
        LAST_CASH_RATIO[symbol] = cash_ratio

        if prev is not None and cash_ratio < 0.8 * prev:
            print(f"[FundamentalsAgent] {symbol} cash ratio dropped: {prev:.2f} → {cash_ratio:.2f}")
            send_event(
                STRATEGY_AGENT_EVENT_URL,
                "fundamentals_alert",
                {"symbol": symbol, "prev_cash_ratio": prev, "new_cash_ratio": cash_ratio}
            )

@app.route("/events", methods=["POST"])
def receive_event():
    """
    Fundamentals Agent does not expect incoming events in this MVP.
    """
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_fundamentals, "interval", hours=24, next_run_time=time.time() + 1)
    scheduler.start()
    print("[FundamentalsAgent] Scheduler started. Listening on port 5004.")
    app.run(host="0.0.0.0", port=5004)
