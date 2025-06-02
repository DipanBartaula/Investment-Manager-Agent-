# Investment Manager (Multi-Agent, Event-Driven)

**Overview**  
This project demonstrates a fully event-driven, multi-agent “Investment Manager.” Each agent runs as a Flask microservice. Agents communicate via:

- **JSON-RPC (MCP-style)** for method/tool calls (e.g., “get latest price,” “fetch fundamentals,” “execute order”).  
- **HTTP POST events (A2A-style)** for asynchronous notifications (e.g., “RSI breached,” “unusual news,” “new strategy,” “approve trade,” “order executed”).

**Agents & Responsibilities**  

1. **Market Data Agent**  
   - Exposes JSON-RPC methods to fetch real-time and historical price data.  
   - All other agents call it when they need raw or aggregated quotes.

2. **Technical Analysis Agent**  
   - Periodically (every 5 minutes) pulls recent price data from Market Data Agent.  
   - Computes RSI and moving averages.  
   - If RSI crosses above 70 or below 30, fires an A2A event to Strategy Agent.

3. **News Agent**  
   - Every hour, fetches latest headlines via a placeholder “fake” news API.  
   - Performs rudimentary sentiment analysis (stubbed).  
   - If sentiment is extremely negative or positive, sends A2A event to Strategy Agent.

4. **Fundamentals Agent**  
   - Once a day, fetches a company’s balance sheet data (using a stub).  
   - Detects anomalies (e.g., sudden drop in cash ratio).  
   - If anomaly found, sends A2A event to Strategy Agent.

5. **Strategy Agent**  
   - Listens for A2A alerts from Technical, News, or Fundamentals Agents.  
   - When an event arrives, calls Market Data Agent via MCP to get up-to-date signals.  
   - Calls OpenAI’s `gpt-4o-mini` to generate a JSON “proposed strategy” (ticker allocations).  
   - Broadcasts the proposed strategy to Risk Agent via A2A.

6. **Risk Agent**  
   - Upon receiving a “new_strategy” event, fetches current portfolio exposure (stubbed).  
   - Checks simple rules (e.g., no single position >20%).  
   - If passes, sends “approve_trade” to Execution Agent; else, “veto_trade.”

7. **Execution Agent**  
   - On “approve_trade,” simulates sending orders to a broker (stubbed).  
   - Once “filled,” sends an “order_executed” A2A event to Compliance Agent.

8. **Compliance Agent**  
   - Logs every “order_executed” event to a local file (e.g., `audit.log`).  
   - Can be extended to enforce further compliance rules.

**How to Run**  

1. **Install Top-Level Dependencies**  
   ```bash
   pip install -r requirements.txt

**Anyone conributing in this open source repo is welcomed to make this agent more efficient and usable in the real market scenario**  
