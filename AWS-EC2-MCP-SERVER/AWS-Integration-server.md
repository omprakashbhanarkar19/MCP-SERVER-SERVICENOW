AWS-Integration-server
--------------------------


python --version


python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

python aws_mcp_server.py

python servicenow_mcp_server.py


curl http://localhost:3333/ec2/list

curl https://dev181732.service-now.com/incident


# Start Server

uvicorn aws_mcp_server:app --host 0.0.0.0 --port 8081 OR

uvicorn aws_mcp_server:app --host 0.0.0.0 --port 3333

uvicorn aws_mcp_server:app --port 4444