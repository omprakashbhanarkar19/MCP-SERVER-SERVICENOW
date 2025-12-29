# from aws_mcp_client import AWSMCPClient
# from servicenow_mcp_client import ServiceNowMCPClient
# from decision_engine import should_restart
# from config import *

# aws = AWSMCPClient(AWS_MCP_URL)
# snow = ServiceNowMCPClient(SNOW_MCP_URL)

# def run_agent():
#     instances = aws.list_instances()

#     for inst in instances:
#         if inst["state"] != "running":
#             continue

#         metrics = aws.get_metrics(inst["instance_id"])
#         cpu = metrics["cpu"]
#         memory = metrics["memory"]

#         print(f"🖥 {inst['instance_id']} CPU={cpu}% MEM={memory}%")

#         if should_restart(cpu, memory):
#             aws.restart_instance(inst["instance_id"])

#             snow.create_incident(
#                 inst["instance_id"],
#                 f"Instance restarted due to CPU={cpu}% Memory={memory}%"
#             )

#             print(f"🔁 Restarted {inst['instance_id']}")

# if __name__ == "__main__":
#     run_agent()


from aws_mcp_client import AWSMCPClient
from servicenow_mcp_client import ServiceNowMCPClient
from decision_engine import should_restart
from config import *

aws = AWSMCPClient(AWS_MCP_URL)
snow = ServiceNowMCPClient(SNOW_MCP_URL)

def run_agent():
    instances = aws.list_instances()

    for inst in instances:
        if inst["state"] != "running":
            continue

        instance_id = inst["instance_id"]
        instance_name = inst.get("name", "N/A")  # 👈 SAFE fallback

        metrics = aws.get_metrics(instance_id)
        cpu = metrics["cpu"]
        memory = metrics["memory"]

        print(
            f"🖥 {instance_name} ({instance_id}) | "
            f"CPU={cpu}% MEM={memory}%"
        )

        if should_restart(cpu, memory):
            aws.restart_instance(instance_id)

            snow.create_incident(
                instance_id,
                f"Instance '{instance_name}' restarted due to "
                f"CPU={cpu}% Memory={memory}%"
            )

            print(f"🔁 Restarted {instance_name} ({instance_id})")

if __name__ == "__main__":
    run_agent()
