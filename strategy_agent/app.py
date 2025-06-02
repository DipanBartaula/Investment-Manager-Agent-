# strategy_agent/app.py

import os
import json
import time
import threading
import requests
from flask import Flask, request, jsonify
from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    MARKET_DATA_AGENT_URL,
    RISK_AGENT_EVENT_URL
)
from mcp_client import MCPClient
from a2a_client import send_event
import openai

app = Flask(__name__)

# Initialize OpenAI key
openai.api_key = OPENAI_API_KEY

# MCP client to Market Data Agent
mcp = MCPClient(MARKET_DATA_AGENT_URL)

def generate_strategy(signals: dict) -> list:
    """
    Calls GPT-4o-mini to produce a JSON strategy based on incoming signals.
    Expected output: [ { "ticker": str, "target_weight": float, "confidence": float }, ... ]
    """
    prompt = (
        "You are an automated portfolio strategist.\n"
        "Given the following signals (technical, news, fundamentals), produce a JSON array of objects:\n"
        "[{ 'ticker': <string>, 'target_weight': <0-1 float>, 'confidence': <0-1 float> }, ...]\n"
        "Do not include any additional text—only the JSON array.\n\n"
        f"Signals:\n{json.dumps(signals, indent=2)}"
    )

    response = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a portfolio strategy assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=500
    )
    content = response.choices[0].message.content.strip()
    try:
        strategy = json.loads(content)
    except json.JSONDecodeError:
        # Fallback: return an equal-weight random strategy
        symbols = ["AAPL", "MSFT", "GOOG"]
        w = 1.0 / len(symbols)
        strategy = [{"ticker": sym, "target_weight": w, "confidence": 0.5} for sym in symbols]
    return strategy

def handle_alert(alert_type: str, data: dict):
    """
    Called whenever a technical/news/fundamentals alert arrives.
    1. Fetch additional data from Market Data (e.g., latest price).  
    2. Compile 'signals' object.  
    3. Call generate_strategy(signals).  
    4. Broadcast 'new_strategy' to Risk Agent.
    """
    # 1. Get latest prices for relevant tickers
    tickers = ["AAPL", "MSFT", "GOOG"]
    prices = {}
    for sym in tickers:
        try:
            res = mcp.call("get_price", {"symbol": sym})
            prices[sym] = res.get("price")
        except Exception as e:
            prices[sym] = None

    # 2. Build signals dict
    signals = {
        "alert_type": alert_type,
        "alert_data": data,
        "prices": prices
    }

    # 3. Call GPT-4o-Mini to generate strategy
    strategy = generate_strategy(signals)
    print(f"[StrategyAgent] Generated strategy: {strategy}")

    # 4. Send A2A event to Risk Agent
    send_event(
        RISK_AGENT_EVENT_URL,
        "new_strategy",
        {"strategy": strategy, "origin": alert_type}
    )
    print("[StrategyAgent] Sent new_strategy to RiskAgent.")

@app.route("/events", methods=["POST"])
def receive_event():
    """
    Receives A2A events from TechnicalAgent, NewsAgent, or FundamentalsAgent.
    Body format: { "type": <string>, "content": <dict> }
    """
    payload = request.get_json()
    alert_type = payload.get("type")
    data = payload.get("content", {})

    # Handle in background thread to avoid blocking HTTP response
    threading.Thread(target=handle_alert, args=(alert_type, data)).start()
    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    print("[StrategyAgent] Listening on port 5005 for A2A events.")
    app.run(host="0.0.0.0", port=5005)




    """      
    { 
    "type": "technical_alert",
      "content": { "ticker": "AAPL",
                    "rsi": 72.5, 
                    "signal": "overbought" 
                 } 
    }

    {
    "type": "news_alert",
      "content": { "sentiment": 0.8, 
                   "alert": "positive" 
                 } 
    }

    {
      "type": "fundamentals_alert",
      "content": { "symbol": "GOOG", 
                   "prev_cash_ratio": 1.2, 
                   "new_cash_ratio": 0.9 
                 } 
    }

    """


