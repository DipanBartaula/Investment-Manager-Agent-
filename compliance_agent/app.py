# compliance_agent/app.py

import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)
AUDIT_LOG = "audit.log"

@app.route("/events", methods=["POST"])
def receive_event():
    """
    Expects: { "type": "order_executed", "content": { "trades": [ {ticker, filled_weight, timestamp}, ... ] } }
    """
    payload = request.get_json()
    evt_type = payload.get("type")
    content = payload.get("content", {})

    if evt_type == "order_executed":
        trades = content.get("trades", [])
        # Append to audit.log
        with open(AUDIT_LOG, "a") as f:
            for trade in trades:
                f.write(json.dumps(trade) + "\n")
        print(f"[ComplianceAgent] Logged {len(trades)} trades.")
        return jsonify({"status": "logged"}), 200
    else:
        return jsonify({"error": "unsupported event type"}), 400

if __name__ == "__main__":
    # Ensure audit log exists
    if not os.path.exists(AUDIT_LOG):
        open(AUDIT_LOG, "w").close()

    print("[ComplianceAgent] Listening on port 5008 for order_executed events.")
    app.run(host="0.0.0.0", port=5008)
