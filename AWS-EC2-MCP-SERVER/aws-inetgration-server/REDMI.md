# Prerequisites

Python 3.9+ (3.11 recommended)

VS Code

AWS MCP Server running

ServiceNow MCP Server running


# Steps:

python --version

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt


# Start AWS MCP Server

python aws_mcp_server.py

# Start ServiceNow MCP Server

python servicenow_mcp_server.py

# Test AWS MCP:

curl http://localhost:3333/ec2/list

# Test ServiceNow MCP:

curl http://localhost:4444/incident/list

# python agent.py

