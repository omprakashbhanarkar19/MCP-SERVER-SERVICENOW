from fastapi import FastAPI, HTTPException
import boto3
from datetime import datetime, timedelta
from typing import List

app = FastAPI(title="AWS MCP Server", version="1.0")

ec2 = boto3.client("ec2")
cloudwatch = boto3.client("cloudwatch")
sts = boto3.client("sts")


# -----------------------------
# Utility: IAM Permission Check
# -----------------------------
@app.get("/iam/validate")
def validate_iam():
    try:
        identity = sts.get_caller_identity()
        return {
            "status": "ok",
            "account": identity["Account"],
            "arn": identity["Arn"]
        }
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))


# -----------------------------
# List EC2 Instances
# -----------------------------
@app.get("/ec2/list")
def list_instances():
    ec2 = boto3.client("ec2")
    response = ec2.describe_instances()

    def get_instance_name(inst):
        for tag in inst.get("Tags", []):
            if tag.get("Key") == "Name":
                return tag.get("Value")
        return inst.get("InstanceId") 


    instances = []
    for reservation in response["Reservations"]:
        for inst in reservation["Instances"]:
            instances.append({
                "instance_id": inst["InstanceId"],
                "state": inst["State"]["Name"],
                "name": get_instance_name(inst),
                "type": inst["InstanceType"],
                "az": inst["Placement"]["AvailabilityZone"],
                #"tags": {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
            })

    return instances


# -----------------------------
# Restart EC2 Instance
# -----------------------------
@app.post("/ec2/restart")
def restart_instance(payload: dict):
    instance_id = payload.get("instance_id")
    if not instance_id:
        raise HTTPException(status_code=400, detail="instance_id is required")

    try:
        ec2.reboot_instances(InstanceIds=[instance_id])
        return {
            "status": "restarted",
            "instance_id": instance_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# CloudWatch Metrics (CPU + Memory)
# -----------------------------
@app.get("/cloudwatch/metrics")
def get_metrics(instance_id: str):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=5)

    # CPU Utilization
    cpu = cloudwatch.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=["Average"]
    )

    cpu_value = (
        cpu["Datapoints"][0]["Average"]
        if cpu["Datapoints"] else 0
    )

    # Memory Utilization (CloudWatch Agent required)
    memory = cloudwatch.get_metric_statistics(
        Namespace="CWAgent",
        MetricName="mem_used_percent",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=["Average"]
    )

    memory_value = (
        memory["Datapoints"][0]["Average"]
        if memory["Datapoints"] else 0
    )

    return {
        "instance_id": instance_id,
        "cpu": round(cpu_value, 2),
        "memory": round(memory_value, 2)
    }


# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health():
    return {"status": "running"}
