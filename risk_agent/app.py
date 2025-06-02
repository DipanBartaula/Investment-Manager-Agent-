# risk_agent/app.py

import os
import json
import threading
from flask import Flask, request, jsonify

from config import EXECUTION_AGENT_EVENT_URL
from a2a_client import send_event

app = Flask(__name__)

# Stub: current portfolio exposures (e.g., from 0.0 to 1.0)
CURRENT_PORTFOLIO = {
    "AAPL": 0.10,
    "MSFT": 0.15,
    "GOOG": 0.05
}

def check_risk_and_respond(strategy_plan: list):
    """
    Risk check: 
      - Ensure no single proposed target_weight > 0.20
      - Ensure sum of all positions ≤ 1.0
      - (More rules can be added.)
    """
    veto_list = []
    total_weight = 0.0
    for leg in strategy_plan:
        tw = leg.get("target_weight", 0.0)
        if tw > 0.20:
            veto_list.append(leg["ticker"])
        total_weight += tw

    if total_weight > 1.0:
        # Over‐allocated
        veto_list.append("OVERALLOCATED")

    if veto_list:
        # Veto
        event_content = {
            "reason": f"Positions {veto_list} breach risk limits",
            "strategy": strategy_plan
        }
        send_event(
            EXECUTION_AGENT_EVENT_URL,
            "veto_trade",
            event_content
        )
        print(f"[RiskAgent] Vetoed strategy: {veto_list}")
    else:
        # Approve
        event_content = { "strategy": strategy_plan }
        send_event(
            EXECUTION_AGENT_EVENT_URL,
            "approve_trade",
            event_content
        )
        print("[RiskAgent] Approved strategy.")

@app.route("/events", methods=["POST"])
def receive_event():
    """
    Expects: { "type": "new_strategy", "content": { "strategy": [ {..}, ... ] } }
    """
    payload = request.get_json()
    evt_type = payload.get("type")
    content = payload.get("content", {})

    if evt_type == "new_strategy":
        strategy = content.get("strategy", [])
        # Spawn background thread to avoid blocking
        threading.Thread(target=check_risk_and_respond, args=(strategy,)).start()
        return jsonify({"status": "processing"}), 200
    else:
        return jsonify({"error": "unsupported event type"}), 400

if __name__ == "__main__":
    print("[RiskAgent] Listening on port 5006 for new_strategy events.")
    app.run(host="0.0.0.0", port=5006)
