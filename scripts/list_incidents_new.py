"""
List ServiceNow incidents with state = New (state=1).

Usage:
  python scripts/list_incidents_new.py

Requires environment variables in .env: SN_INSTANCE, SN_USERNAME, SN_PASSWORD, SN_API_VERSION (optional)
"""

import os
import sys
import httpx
from dotenv import load_dotenv

load_dotenv()

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
    timeout=30
)


def _sn_request(method: str, url: str, **kwargs):
    resp = client.request(method, url, **kwargs)
    resp.raise_for_status()
    return resp.json().get("result")


def list_new_incidents(limit: int = 50):
    # Use numeric state=1 (New) which is common in ServiceNow
    params = {"sysparm_query": "state=1", "sysparm_limit": limit}
    return _sn_request("GET", "/table/incident", params=params)


def main():
    incidents = list_new_incidents(limit=100)
    if not incidents:
        print("No incidents in state=New found.")
        return
    print(f"Found {len(incidents)} incident(s) in state=New:")
    for i, inc in enumerate(incidents, start=1):
        number = inc.get("number")
        sys_id = inc.get("sys_id")
        short = inc.get("short_description")
        priority = inc.get("priority")
        state = inc.get("state") or inc.get("incident_state")
        created = inc.get("sys_created_on")
        print(f"{i}. {number} | sys_id={sys_id} | priority={priority} | state={state} | created={created}\n   {short}")


if __name__ == "__main__":
    main()
