"""
Create a P9 incident (urgency=3, impact=3) for a given user.

Usage:
  python scripts/create_p9_incident.py --sys-id 6816f79cc0a8016400b98a06818d57fd --short "API outage"
  python scripts/create_p9_incident.py --user some.username --short "API outage"

Requires environment variables in .env: SN_INSTANCE, SN_USERNAME, SN_PASSWORD, SN_API_VERSION (optional)
"""

import os
import sys
import argparse
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

try:
    from servicenow_mcp_server import create_incident as create_incident_tool
except Exception:
    create_incident_tool = None

SN_INSTANCE = os.getenv("SN_INSTANCE")
SN_USERNAME = os.getenv("SN_USERNAME")
SN_PASSWORD = os.getenv("SN_PASSWORD")
SN_API_VERSION = os.getenv("SN_API_VERSION", "now")

if not all([SN_INSTANCE, SN_USERNAME, SN_PASSWORD]):
    print("Missing ServiceNow configuration in environment variables.")
    sys.exit(1)

client = httpx.Client(
    base_url=f"{SN_INSTANCE}/api/{SN_API_VERSION}",
    auth=(SN_USERNAME, SN_PASSWORD),
    headers={"Accept": "application/json", "Content-Type": "application/json"},
    timeout=30,
)


def _sn_request(method: str, url: str, **kwargs):
    resp = client.request(method, url, **kwargs)
    resp.raise_for_status()
    return resp.json().get("result")


def get_user_sys_id(user_name: str):
    params = {"sysparm_query": f"user_name={user_name}", "sysparm_limit": 1}
    res = _sn_request("GET", "/table/sys_user", params=params)
    if isinstance(res, list) and len(res) > 0:
        return res[0].get("sys_id")
    if isinstance(res, dict) and res.get("sys_id"):
        return res.get("sys_id")
    return None


def create_p9_incident(caller_sys_id: str, short_description: str):
    payload = {
        "caller_id": caller_sys_id,
        "short_description": short_description,
        "urgency": "3",
        "impact": "3"
    }
    if create_incident_tool:
        # Use the existing tool if available (it expects more args, so pass minimal values)
        return create_incident_tool(short_description=short_description, description=short_description, caller_id=caller_sys_id, urgency="3", impact="3")
    # Fallback to direct API
    return _sn_request("POST", "/table/incident", json=payload)


def main():
    parser = argparse.ArgumentParser(description="Create a P9 incident (urgency=3, impact=3)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sys-id", help="Caller sys_id")
    group.add_argument("--user", help="Caller user_name to look up sys_id")
    parser.add_argument("--short", default="API outage", help="Short description")
    args = parser.parse_args()

    if args.user:
        print(f"Looking up user '{args.user}'...")
        caller = get_user_sys_id(args.user)
        if not caller:
            print(f"User '{args.user}' not found.")
            sys.exit(1)
    else:
        caller = args.sys_id

    print(f"Creating P9 incident for caller {caller} with short description: '{args.short}'")
    incident = create_p9_incident(caller, args.short)
    print("Incident created:")
    try:
        print(json.dumps(incident, indent=2))
    except Exception:
        print(incident)


if __name__ == "__main__":
    main()
