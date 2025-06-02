#!/usr/bin/env bash
#
# start_agents.sh
#
# This script navigates into the InvestmentManager project folder,
# installs dependencies for each agent, and launches them in the background.
#
# Usage:
#   1. Place this script at the root of your cloned repo (next to README.md).
#   2. Make it executable: chmod +x start_agents.sh
#   3. Run: ./start_agents.sh
#

set -euo pipefail

# 1. Navigate to the root of the project directory
#    (Assumes this script is located in the InvestmentManager/ folder)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== InvestmentManager root directory: $PWD ==="

# 2. (Optional) Activate a virtual environment if you use one
#    Uncomment and adjust the following lines if needed.
# echo "Activating virtual environment..."
# source ./venv/bin/activate

# 3. Export environment variables (e.g., API keys)
#    Replace placeholders with your actual keys, or ensure they’re set in your shell already.
export OPENAI_API_KEY="your_openai_api_key_here"
export NEWS_API_KEY="your_news_api_key_here"
echo "Environment variables set (OPENAI_API_KEY, NEWS_API_KEY)."

# 4. Start each agent in turn. We install requirements then run app.py in the background.
#    Logs for each agent will be redirected to a file in the agent’s folder for easy debugging.

########################################
# 4.1 Market Data Agent
########################################
echo "---- Starting Market Data Agent (port 5001) ----"
cd "$SCRIPT_DIR/market_data_agent"
pip install -r requirements.txt
# Launch in background; redirect stdout/stderr to market_data_agent.log
nohup python app.py > market_data_agent.log 2>&1 &
MARKET_PID=$!
echo "Market Data Agent launched (PID=$MARKET_PID)."

########################################
# 4.2 Technical Analysis Agent
########################################
echo "---- Starting Technical Analysis Agent (port 5002) ----"
cd "$SCRIPT_DIR/technical_analysis_agent"
pip install -r requirements.txt
nohup python app.py > technical_analysis_agent.log 2>&1 &
TECH_PID=$!
echo "Technical Analysis Agent launched (PID=$TECH_PID)."

########################################
# 4.3 News Agent
########################################
echo "---- Starting News Agent (port 5003) ----"
cd "$SCRIPT_DIR/news_agent"
pip install -r requirements.txt
nohup python app.py > news_agent.log 2>&1 &
NEWS_PID=$!
echo "News Agent launched (PID=$NEWS_PID)."

########################################
# 4.4 Fundamentals Agent
########################################
echo "---- Starting Fundamentals Agent (port 5004) ----"
cd "$SCRIPT_DIR/fundamentals_agent"
pip install -r requirements.txt
nohup python app.py > fundamentals_agent.log 2>&1 &
FUND_PID=$!
echo "Fundamentals Agent launched (PID=$FUND_PID)."

########################################
# 4.5 Strategy Agent
########################################
echo "---- Starting Strategy Agent (port 5005) ----"
cd "$SCRIPT_DIR/strategy_agent"
pip install -r requirements.txt
nohup python app.py > strategy_agent.log 2>&1 &
STRAT_PID=$!
echo "Strategy Agent launched (PID=$STRAT_PID)."

########################################
# 4.6 Risk Agent
########################################
echo "---- Starting Risk Agent (port 5006) ----"
cd "$SCRIPT_DIR/risk_agent"
pip install -r requirements.txt
nohup python app.py > risk_agent.log 2>&1 &
RISK_PID=$!
echo "Risk Agent launched (PID=$RISK_PID)."

########################################
# 4.7 Execution Agent
########################################
echo "---- Starting Execution Agent (port 5007) ----"
cd "$SCRIPT_DIR/execution_agent"
pip install -r requirements.txt
nohup python app.py > execution_agent.log 2>&1 &
EXEC_PID=$!
echo "Execution Agent launched (PID=$EXEC_PID)."

########################################
# 4.8 Compliance Agent
########################################
echo "---- Starting Compliance Agent (port 5008) ----"
cd "$SCRIPT_DIR/compliance_agent"
pip install -r requirements.txt
nohup python app.py > compliance_agent.log 2>&1 &
COMP_PID=$!
echo "Compliance Agent launched (PID=$COMP_PID)."

########################################
# 5. Return to project root
########################################
cd "$SCRIPT_DIR"
echo "All agents started. Return to $PWD to view logs:"

echo "  Market Data Agent log:             market_data_agent/market_data_agent.log"
echo "  Technical Analysis Agent log:       technical_analysis_agent/technical_analysis_agent.log"
echo "  News Agent log:                     news_agent/news_agent.log"
echo "  Fundamentals Agent log:             fundamentals_agent/fundamentals_agent.log"
echo "  Strategy Agent log:                 strategy_agent/strategy_agent.log"
echo "  Risk Agent log:                     risk_agent/risk_agent.log"
echo "  Execution Agent log:                execution_agent/execution_agent.log"
echo "  Compliance Agent log:               compliance_agent/compliance_agent.log"

echo
echo "PIDs:"
echo "  Market Data Agent:        $MARKET_PID"
echo "  Technical Analysis Agent: $TECH_PID"
echo "  News Agent:               $NEWS_PID"
echo "  Fundamentals Agent:       $FUND_PID"
echo "  Strategy Agent:           $STRAT_PID"
echo "  Risk Agent:               $RISK_PID"
echo "  Execution Agent:          $EXEC_PID"
echo "  Compliance Agent:         $COMP_PID"
echo
echo "Use 'kill <PID>' to stop any agent, or run 'pkill -f app.py' to kill all."
