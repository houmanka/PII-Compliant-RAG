"""
Test trigger script — creates topic/sub if needed, generates a fresh CSV, and publishes an event.

Usage:
    uv run python ./localdev/trigger_test.py
"""
import json
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path

PUBSUB_EMULATOR_HOST = "localhost:8085"
GOOGLE_CLOUD_PROJECT = "local"
TOPIC = "object-created"
SUBSCRIPTION = "object-created-sub"
INBOX = Path(__file__).parents[1] / "data" / "inbox"
TEMPLATE = INBOX / "test_template.csv"


def run(cmd: str) -> int:
    env = os.environ.copy()
    env["PUBSUB_EMULATOR_HOST"] = PUBSUB_EMULATOR_HOST
    env["GOOGLE_CLOUD_PROJECT"] = GOOGLE_CLOUD_PROJECT
    result = subprocess.run(cmd, shell=True, env=env)
    return result.returncode


def setup_pubsub():
    print("Setting up Pub/Sub topic and subscription...")
    run(f"uv run python ./localdev/pubsub_emulator_tools.py create-topic --topic {TOPIC}")
    run(f"uv run python ./localdev/pubsub_emulator_tools.py create-sub --topic {TOPIC} --subscription {SUBSCRIPTION}")


def generate_csv() -> Path:
    sample_num = random.randint(1000, 9999)
    dest = INBOX / f"sample_{sample_num}.csv"

    lines = TEMPLATE.read_text().splitlines()
    header = lines[0]
    data_rows = lines[1:]

    new_rows = []
    for row in data_rows:
        new_case_id = random.randint(10_000_000, 99_999_999)
        # replace only the case_id (first field)
        _, narrative = row.split(",", 1)
        new_rows.append(f"{new_case_id},{narrative}")

    dest.write_text("\n".join([header] + new_rows) + "\n")
    print(f"Generated: {dest.name}")
    return dest


def publish(csv_path: Path):
    payload = json.dumps({
        "provider": "local",
        "path": f"data/inbox/{csv_path.name}",
        "eventType": "ObjectCreated",
    })
    print(f"Publishing event for: {csv_path.name}")
    rc = run(f"uv run python ./localdev/pubsub_emulator_tools.py publish --topic {TOPIC} --json '{payload}'")
    if rc != 0:
        print("Publish failed — is the emulator running?", file=sys.stderr)
        sys.exit(1)
    print("Done.")


if __name__ == "__main__":
    setup_pubsub()
    csv_path = generate_csv()
    publish(csv_path)
