# mcp_client.py

import requests
import json

class MCPClient:
    """
    Simple JSON-RPC 2.0 client. To call remote methods on another agent, use:
        client = MCPClient("http://127.0.0.1:5001/rpc")
        result = client.call("methodName", {"param1": "value1", ...})
    """

    def __init__(self, url: str):
        self.url = url
        self._request_id = 1

    def call(self, method: str, params: dict):
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self._request_id
        }
        self._request_id += 1
        response = requests.post(self.url, json=payload)
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise RuntimeError(f"JSON-RPC error: {data['error']}")
        return data.get("result")
