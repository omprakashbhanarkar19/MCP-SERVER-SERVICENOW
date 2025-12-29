"""
ServiceNow MCP Server
Author: Omprakash Bhanarkar
Description:
MCP server exposing ServiceNow APIs as tools for LLM agents
"""

import os
from typing import Optional, List
import httpx
from dotenv import load_dotenv
import sys
from mcp.server.fastmcp import FastMCP

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------
load_dotenv()

SN_INSTANCE = os.getenv("SN_INSTANCE")  # https://dev12345.service-now.com
SN_USERNAME = os.getenv("SN_USERNAME")
SN_PASSWORD = os.getenv("SN_PASSWORD")
SN_API_VERSION = os.getenv("SN_API_VERSION", "now")

if not all([SN_INSTANCE, SN_USERNAME, SN_PASSWORD]):
    raise RuntimeError("Missing ServiceNow configuration")

# --------------------------------------------------
# Initialize MCP Server
# --------------------------------------------------
mcp = FastMCP(
    name="servicenow-mcp",
    #description="ServiceNow MCP Server exposing Incident, Change, Request, and CMDB operations"
)

# --------------------------------------------------
# HTTP Client
# --------------------------------------------------
client = httpx.Client(
    base_url=f"{SN_INSTANCE}/api/{SN_API_VERSION}",
    auth=(SN_USERNAME, SN_PASSWORD),
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json"
    },
    timeout=30
)

# --------------------------------------------------
# Utility Function
# --------------------------------------------------
def _sn_request(method: str, url: str, **kwargs):
    response = client.request(method, url, **kwargs)
    response.raise_for_status()
    return response.json()["result"]

# ==================================================
# INCIDENT MANAGEMENT
# ==================================================

@mcp.tool()
def create_incident(
    short_description: str,
    description: str,
    caller_id: Optional[str] = None,
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    impact: str = "3",
    urgency: str = "3",
    priority: str = "3",
    assignment_group: Optional[str] = None,
    assigned_to: Optional[str] = None,
    state: Optional[str] = None
) -> dict:
    """
    Create a ServiceNow Incident with full details
    """
    payload = {
        "short_description": short_description,
        "description": description,
        "caller_id": caller_id,
        "category": category,
        "subcategory": subcategory,
        "impact": impact,
        "urgency": urgency,
        "priority": priority,
        "assignment_group": assignment_group,
        "assigned_to": assigned_to,
        "state": state
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    return _sn_request("POST", "/table/incident", json=payload)


@mcp.tool()
def list_new_incidents(limit: int = 10) -> list:
    """
    List NEW ServiceNow incidents (state = New)
    """
    params = {
        "sysparm_query": "state=1",
        "sysparm_limit": limit,
        "sysparm_order_by": "-sys_created_on"
    }
    return _sn_request("GET", "/table/incident", params=params)

@mcp.tool()
def list_open_incidents(limit: int = 10) -> list:
    """
    List OPEN ServiceNow incidents (active=true)
    """
    params = {
        "sysparm_query": "active=true",
        "sysparm_limit": limit,
        "sysparm_order_by": "-sys_created_on"
    }
    return _sn_request("GET", "/table/incident", params=params)   


@mcp.tool()
def list_closed_incidents(limit: int = 10) -> list:
    """
    List CLOSED ServiceNow incidents (state = Closed)
    """
    params = {
        "sysparm_query": "state=7",
        "sysparm_limit": limit,
        "sysparm_order_by": "-closed_at"
    }
    return _sn_request("GET", "/table/incident", params=params)



@mcp.tool()
def get_incident(sys_id: str) -> dict:
    """
    Get an Incident by sys_id
    """
    return _sn_request("GET", f"/table/incident/{sys_id}")


@mcp.tool()
def search_incidents(
    query: str,
    limit: int = 10
) -> List[dict]:
    """
    Search incidents using encoded query
    """
    params = {
        "sysparm_query": query,
        "sysparm_limit": limit
    }
    return _sn_request("GET", "/table/incident", params=params)

# ==================================================
# CHANGE MANAGEMENT
# ==================================================

@mcp.tool()
def create_change_request(
    short_description: str,
    description: str,
    change_type: str = "normal",
    risk: str = "3",
    impact: str = "3",
    assignment_group: Optional[str] = None
) -> dict:
    """
    Create a Change Request
    """
    payload = {
        "short_description": short_description,
        "description": description,
        "type": change_type,
        "risk": risk,
        "impact": impact,
        "assignment_group": assignment_group
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    return _sn_request("POST", "/table/change_request", json=payload)

# ==================================================
# REQUEST / SERVICE CATALOG
# ==================================================

@mcp.tool()
def list_catalog_items(limit: int = 10) -> List[dict]:
    """
    List Service Catalog Items
    """
    params = {"sysparm_limit": limit}
    return _sn_request("GET", "/table/sc_cat_item", params=params)


@mcp.tool()
def create_request(
    short_description: str,
    requested_for: Optional[str] = None
) -> dict:
    """
    Create a Service Request (REQ)
    """
    payload = {
        "short_description": short_description,
        "requested_for": requested_for
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    return _sn_request("POST", "/table/sc_request", json=payload)

# ==================================================
# CMDB
# ==================================================

@mcp.tool()
def get_cmdb_ci(
    sys_id: Optional[str] = None,
    name: Optional[str] = None
) -> List[dict]:
    """
    Retrieve CMDB Configuration Items
    """
    query = []
    if sys_id:
        query.append(f"sys_id={sys_id}")
    if name:
        query.append(f"nameLIKE{name}")

    params = {
        "sysparm_query": "^".join(query),
        "sysparm_limit": 10
    }
    return _sn_request("GET", "/table/cmdb_ci", params=params)

# ==================================================
# USERS
# ==================================================

@mcp.tool()
def get_user(
    user_name: Optional[str] = None,
    email: Optional[str] = None
) -> List[dict]:
    """
    Get ServiceNow users
    """
    query = []
    if user_name:
        query.append(f"user_name={user_name}")
    if email:
        query.append(f"email={email}")

    params = {
        "sysparm_query": "^".join(query),
        "sysparm_limit": 5
    }
    return _sn_request("GET", "/table/sys_user", params=params)

# # # ==================================================
# # # PRINT HELPERS
# # # ==================================================

def print_new_incidents():
    """Print new incidents to console"""
    incidents = list_new_incidents()
    for incident in incidents:
        print(incident)

def print_open_incidents():
    """Print open incidents to console"""
    incidents = list_open_incidents()
    for incident in incidents:
        print(incident)

def print_closed_incidents():
    """Print closed incidents to console"""
    incidents = list_closed_incidents()
    for incident in incidents:
        print(incident)

# ==================================================
# SERVER START
# ==================================================

if __name__ == "__main__":

    # Run as CLI (VS Code terminal)
    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "new":
            print_new_incidents()
        elif cmd == "open":
            print_open_incidents()
        elif cmd == "closed":
            print_closed_incidents()
        else:
            print("Usage: python servicenow-mcp_server.py [new|open|closed]")
    else:
        # Run as MCP server

        mcp.run()


# def print_new_incidents():
#     print("Printing NEW incidents...")

# def print_open_incidents():
#     print("Printing OPEN incidents...")

# def print_closed_incidents():
#     print("Printing CLOSED incidents...")

# def run_server():
#     # Replace with your actual server startup, e.g., mcp.run()
#     print("Starting MCP server...")

# if __name__ == "__main__":
#     # Run as CLI (VS Code terminal)
#     if len(sys.argv) > 1:
#         cmd = sys.argv[1].lower()
#         if cmd == "new":
#             print_new_incidents()
#         elif cmd == "open":
#             print_open_incidents()
#         elif cmd == "closed":
#             print_closed_incidents()
#         else:
#             print("Usage: python servicenow-mcp_server.py [new|open|closed]")
#     else:
#                # Run as MCP server
#         mcp.run()