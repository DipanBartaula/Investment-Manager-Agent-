# technical_analysis_agent/app.py

import os
import time
import json
import requests
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import numpy as np

from mcp_client import MCPClient
from a2a_client import send_event
from config import MARKET_DATA_AGENT_URL, STRATEGY_AGENT_EVENT_URL

app = Flask(__name__)

# List of tickers to monitor
TICKERS = ["AAPL", "MSFT", "GOOG"]

# Store last RSI to detect crossovers
LAST_RSI = {ticker: None for ticker in TICKERS}

# MCP client to Market Data Agent
mcp = MCPClient(MARKET_DATA_AGENT_URL)

def compute_rsi(prices: pd.Series, window: int = 14) -> float:
    """
    Compute RSI (Relative Strength Index) on a series of closing prices.
    RSI = 100 - (100 / (1 + RS)), where RS = avg gain / avg loss over window.
    """
    deltas = prices.diff().dropna()
    gain = deltas.where(deltas > 0, 0.0)
    loss = -deltas.where(deltas < 0, 0.0)

    avg_gain = gain.rolling(window).mean().iloc[-1]
    avg_loss = loss.rolling(window).mean().iloc[-1]
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return float(rsi)

def check_technical():
    """
    Scheduled job (every 5 min):
      1. Fetch last 30 days of daily close for each ticker.
      2. Compute RSI.
      3. If RSI crosses above 70 (overbought) or below 30 (oversold),
         send an A2A event to Strategy Agent.
    """
    global LAST_RSI
    for ticker in TICKERS:
        # 1. Get 30-day daily historical data via MCP
        try:
            resp = mcp.call("get_historical", {"symbol": ticker, "period": "30d", "interval": "1d"})
            history = resp.get("history", [])
            if not history:
                continue
            closes = pd.Series([h["close"] for h in history])
            # 2. Compute RSI
            rsi = compute_rsi(closes, window=14)
        except Exception as e:
            print(f"[TechnicalAgent] Error fetching data for {ticker}: {e}")
            continue

        prev = LAST_RSI.get(ticker)
        LAST_RSI[ticker] = rsi

        # 3. Detect crossover
        #    If prev exists, and for example, prev < 70 and now >= 70 → overbought
        #    Or prev > 30 and now <= 30 → oversold
        if prev is not None:
            if prev < 70 and rsi >= 70:
                print(f"[TechnicalAgent] {ticker} RSI crossed above 70: {rsi:.2f}")
                send_event(
                    STRATEGY_AGENT_EVENT_URL,
                    "technical_alert",
                    {"ticker": ticker, "rsi": rsi, "signal": "overbought"}
                )
            elif prev > 30 and rsi <= 30:
                print(f"[TechnicalAgent] {ticker} RSI crossed below 30: {rsi:.2f}")
                send_event(
                    STRATEGY_AGENT_EVENT_URL,
                    "technical_alert",
                    {"ticker": ticker, "rsi": rsi, "signal": "oversold"}
                )

@app.route("/events", methods=["POST"])
def receive_event():
    """
    Technical Agent doesn’t expect incoming events in this MVP.
    We include the endpoint so POSTs don’t 404.
    """
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # Schedule check_technical every 5 minutes
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_technical, "interval", minutes=5, next_run_time=time.time() + 1)
    scheduler.start()
    print("[TechnicalAgent] Scheduler started. Listening on port 5002.")
    app.run(host="0.0.0.0", port=5002)
