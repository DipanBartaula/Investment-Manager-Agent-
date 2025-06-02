# config.py

import os

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_KEY")
OPENAI_MODEL = "gpt-4o-mini"

# News API (stubbed)
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "YOUR_NEWS_API_KEY")

# Agent URLs (for MCP / A2A discovery)
MARKET_DATA_AGENT_URL = "http://127.0.0.1:5001/rpc"
TECHNICAL_AGENT_EVENT_URL = "http://127.0.0.1:5002/events"
NEWS_AGENT_EVENT_URL = "http://127.0.0.1:5003/events"
FUNDAMENTALS_AGENT_EVENT_URL = "http://127.0.0.1:5004/events"
STRATEGY_AGENT_EVENT_URL = "http://127.0.0.1:5005/events"
RISK_AGENT_EVENT_URL = "http://127.0.0.1:5006/events"
EXECUTION_AGENT_EVENT_URL = "http://127.0.0.1:5007/events"
COMPLIANCE_AGENT_EVENT_URL = "http://127.0.0.1:5008/events"
