import requests

class AWSMCPClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def list_instances(self):
        return requests.get(f"{self.base_url}/ec2/list").json()

    def get_metrics(self, instance_id):
        return requests.get(
            f"{self.base_url}/cloudwatch/metrics",
            params={"instance_id": instance_id}
        ).json()

    def restart_instance(self, instance_id):
        return requests.post(
            f"{self.base_url}/ec2/restart",
            json={"instance_id": instance_id}
        ).json()
