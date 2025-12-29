import requests

class ServiceNowMCPClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def create_incident(self, instance_id, message):
        payload = {
            "short_description": f"EC2 Auto-Restart: {instance_id}",
            "description": message,
            "severity": "2"
        }
        return requests.post(
            f"{self.base_url}/incident/create",
            json=payload
        ).json()
