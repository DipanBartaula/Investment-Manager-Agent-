# execution_agent/app.py

import os
import time
import threading
from flask import Flask, request, jsonify

from config import COMPLIANCE_AGENT_EVENT_URL
from a2a_client import send_event

app = Flask(__name__)

def execute_orders(strategy_plan: list):
    """
    Simulates sending orders to a broker. 
    For each leg, we “sleep” 1 second and then mark as “filled.”
    Finally, send order_executed event to Compliance Agent.
    """
    executed_trades = []
    for leg in strategy_plan:
        ticker = leg["ticker"]
        weight = leg["target_weight"]
        # Simulate time to send order / wait for fill
        print(f"[ExecutionAgent] Placing order for {ticker} at weight {weight:.2f} ...")
        time.sleep(1)  # simulate latency
        executed_trades.append({
            "ticker": ticker,
            "filled_weight": weight,
            "timestamp": time.time()
        })

    # Once all “filled,” send order_executed to ComplianceAgent
    send_event(
        COMPLIANCE_AGENT_EVENT_URL,
        "order_executed",
        {"trades": executed_trades}
    )
    print("[ExecutionAgent] Sent order_executed event to ComplianceAgent.")

@app.route("/events", methods=["POST"])
def receive_event():
    """
    Expects:
      - { "type": "approve_trade", "content": { "strategy": [ ... ] } }
      - { "type": "veto_trade", "content": { "reason": "...", "strategy": [ ... ] } }
    """
    payload = request.get_json()
    evt_type = payload.get("type")
    content = payload.get("content", {})

    if evt_type == "approve_trade":
        strategy = content.get("strategy", [])
        threading.Thread(target=execute_orders, args=(strategy,)).start()
        return jsonify({"status": "executing"}), 200

    elif evt_type == "veto_trade":
        reason = content.get("reason", "no reason provided")
        print(f"[ExecutionAgent] Trade vetoed: {reason}")
        return jsonify({"status": "vetoed"}), 200

    else:
        return jsonify({"error": "unsupported event type"}), 400

if __name__ == "__main__":
    print("[ExecutionAgent] Listening on port 5007 for trade events.")
    app.run(host="0.0.0.0", port=5007)
