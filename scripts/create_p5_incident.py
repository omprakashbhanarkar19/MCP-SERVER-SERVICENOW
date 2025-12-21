"""
Create a P5 incident for user 'qwertyuiop' with short description 'Omprakash_task_created by persnal'.

Usage:
    python scripts/create_p5_incident.py

Requires environment variables in .env: SN_INSTANCE, SN_USERNAME, SN_PASSWORD, SN_API_VERSION (optional)
"""

import os
import sys
import httpx
from dotenv import load_dotenv
try:
    from servicenow import create_record
except Exception:
    create_record = None

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


def create_incident(caller_sys_id: str, short_description: str, urgency: str = "4", impact: str = "4"):
    payload = {
        "caller_id": caller_sys_id,
        "short_description": short_description,
        "urgency": urgency,
        "impact": impact
    }
    if create_record:
        return create_record("incident", payload)
    return _sn_request("POST", "/table/incident", json=payload)


if __name__ == "__main__":
    target_user = "qwertyuiop"
    short_desc = "Omprakash_task_created by persnal"

    print(f"Looking up user '{target_user}'...")
    user_sys_id = get_user_sys_id(target_user)
    if not user_sys_id:
        print(f"User '{target_user}' not found. Exiting.")
        sys.exit(1)

    print(f"Creating P5 incident for user '{target_user}' ({user_sys_id})...")
    incident = create_incident(user_sys_id, short_desc, urgency="4", impact="4")
    print("Incident created:")
    print(incident)
