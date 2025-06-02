# a2a_client.py

import requests
import json

def send_event(target_url: str, event_type: str, content: dict):
    """
    Sends an HTTP POST to target_url with JSON body:
    {
      "type": event_type,
      "content": { ... }
    }
    """
    payload = {
        "type": event_type,
        "content": content
    }
    resp = requests.post(target_url, json=payload)
    resp.raise_for_status()
    return resp.json() if resp.text else {}

