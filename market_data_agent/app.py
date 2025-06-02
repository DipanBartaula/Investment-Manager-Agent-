# market_data_agent/app.py

from flask import Flask, request, jsonify
from jsonrpcserver import methods
import yfinance as yf
import pandas as pd

app = Flask(__name__)

# In-memory cache to avoid repeated downloads
CACHE = {}

@methods.add
def get_price(symbol: str) -> dict:
    """
    JSON-RPC method: get the latest price for a ticker via yfinance.
    Returns: { "symbol": str, "price": float, "timestamp": ISO8601 }
    """
    # Use yfinance to fetch real-time price (or close of last day if off-hours)
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d", interval="1m")
    if data.empty:
        return { "symbol": symbol, "error": "No data" }
    last_row = data.iloc[-1]
    price = float(last_row["Close"])
    timestamp = last_row.name.to_pydatetime().isoformat()
    return { "symbol": symbol, "price": price, "timestamp": timestamp }

@methods.add
def get_historical(symbol: str, period: str = "1mo", interval: str = "1d") -> dict:
    """
    JSON-RPC method: get historical OHLC data.
    Returns a dict with dates and closing prices for simplicity.
    """
    df = yf.download(tickers=symbol, period=period, interval=interval, progress=False)
    if df.empty:
        return { "symbol": symbol, "history": [] }
    history = []
    for dt, row in df.iterrows():
        history.append({
            "date": dt.to_pydatetime().strftime("%Y-%m-%d"),
            "close": float(row["Close"])
        })
    return { "symbol": symbol, "history": history }

@app.route("/rpc", methods=["POST"])
def rpc_server():
    request_json = request.get_data().decode()
    response = methods.dispatch(request_json)
    return jsonify(response)

if __name__ == "__main__":
    # Run on port 5001
    app.run(host="0.0.0.0", port=5001)
