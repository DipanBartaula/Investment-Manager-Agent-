# market_data_agent.py

from flask import Flask, request, jsonify
import jsonrpcserver  # pip install jsonrpcserver

app = Flask(__name__)

# In-memory stub of live prices
FAKE_MARKET_DB = {
    "AAPL": 174.32,
    "GOOG": 2865.50,
    "MSFT": 310.12
}

def get_price(symbol: str):
    price = FAKE_MARKET_DB.get(symbol.upper())
    if price is None:
        raise ValueError(f"Symbol {symbol} not found")
    return {"symbol": symbol.upper(), "price": price, "timestamp": "2025-06-01T15:30:00Z"}

def get_historical(symbol: str, days: int):
    # Stub: return fake historical candles
    hist = [{"date": f"2025-05-{d+1:02d}", "close": FAKE_MARKET_DB[symbol.upper()] - d*0.5} 
            for d in range(days)]
    return {"symbol": symbol.upper(), "history": hist}

@app.route("/rpc", methods=["POST"])
def rpc_handler():
    request_json = request.get_data().decode()
    response = jsonrpcserver.dispatch(request_json, methods=[get_price, get_historical])
    return jsonify(response)

if __name__ == "__main__":
    # Runs on port 5001
    app.run(host="0.0.0.0", port=5001)











#This is a rough implementaion of accessing data later it will be replaced with a real market data provider
# Note: This is a simple in-memory database for demonstration purposes.
