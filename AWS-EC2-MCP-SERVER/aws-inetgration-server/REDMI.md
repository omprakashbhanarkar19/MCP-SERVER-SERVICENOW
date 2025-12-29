# AWS Ec2 MCP Server 

# Prerequisites

Python 3.9+ (3.11 recommended)

VS Code

AWS MCP Server running

ServiceNow MCP Server running


# Steps:

configure aws cli

aws configure 

# Create Virtual Environment

python --version

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt


# Start AWS MCP Server

python aws_mcp_server.py

# Start ServiceNow MCP Server

python servicenow_mcp_server.py


# Start Server


uvicorn aws_mcp_server:app --host 0.0.0.0 --port 3333  # AWS EC2 MCP Server

uvicorn aws_mcp_server:app --port 4444  # ServiceNoe MCP Server


# Test AWS MCP:

curl http://localhost:3333/ec2/list   # aws ec2 server

# Test ServiceNow MCP:

curl http://localhost:4444/incident/list # Service Now server

# RUN and Check Output

python agent.py

