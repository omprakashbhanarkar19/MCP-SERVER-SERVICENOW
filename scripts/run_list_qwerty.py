"""
Run a ServiceNow query to list incidents for user 'qwertyuiop'.

Usage:
  python scripts/run_list_qwerty.py

Requires .env with SN_INSTANCE, SN_USERNAME, SN_PASSWORD, SN_API_VERSION (optional)
"""
import os
import sys
import json
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


def get_user_sys_id(user_name: str):
    params = {"sysparm_query": f"user_name={user_name}", "sysparm_limit": 1}
    res = _sn_request("GET", "/table/sys_user", params=params)
    if isinstance(res, list) and len(res) > 0:
        return res[0].get("sys_id")
    if isinstance(res, dict) and res.get("sys_id"):
        return res.get("sys_id")
    return None


def list_incidents_for_caller(caller_sys_id: str, limit: int = 50):
    params = {"sysparm_query": f"caller_id={caller_sys_id}", "sysparm_limit": limit}
    return _sn_request("GET", "/table/incident", params=params)


def main():
    target_user = "qwertyuiop"
    print(f"Looking up user '{target_user}'...")
    caller_sys = get_user_sys_id(target_user)
    if not caller_sys:
        print(f"User '{target_user}' not found.")
        return
    print(f"Found caller sys_id: {caller_sys}. Querying incidents...")
    incidents = list_incidents_for_caller(caller_sys, limit=100)
    if not incidents:
        print(f"No incidents found for {target_user} (caller_id={caller_sys}).")
        return
    print(f"Found {len(incidents)} incident(s) for {target_user} (caller_id={caller_sys}):")
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
