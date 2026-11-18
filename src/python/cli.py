import argparse
import sys
import json
import httpx

BASE_URL = "http://127.0.0.1:8000"

def cmd_intercept(args):
    payload = {
        "session_id": args.session_id,
        "tool_name": args.tool,
        "raw_input": args.input,
        "context_metadata": {
            "domain": args.domain,
            "classification": args.classification,
            "authorized_clearance": args.clearance
        }
    }
    try:
        response = httpx.post(f"{BASE_URL}/intercept", json=payload, timeout=5.0)
        print(f"\n[HTTP Status: {response.status_code}]")
        print(json.dumps(response.json(), indent=2))
    except httpx.ConnectError:
        print(f"[Error] Could not connect to gateway at {BASE_URL}. Ensure uvicorn is running.")

def cmd_session(args):
    try:
        response = httpx.get(f"{BASE_URL}/sessions/{args.session_id}", timeout=5.0)
        print(f"\n[HTTP Status: {response.status_code}]")
        print(json.dumps(response.json(), indent=2))
    except httpx.ConnectError:
        print(f"[Error] Could not connect to gateway at {BASE_URL}.")

def cmd_policies(args):
    try:
        response = httpx.get(f"{BASE_URL}/policies", timeout=5.0)
        print(f"\n[HTTP Status: {response.status_code}]")
        print(json.dumps(response.json(), indent=2))
    except httpx.ConnectError:
        print(f"[Error] Could not connect to gateway at {BASE_URL}.")

def main():
    parser = argparse.ArgumentParser(description="Contextual Harmony Interactive CLI Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Intercept command
    p_intercept = subparsers.add_parser("intercept", help="Send a simulated tool call to the gateway")
    p_intercept.add_argument("--tool", required=True, help="Name of the tool being executed")
    p_intercept.add_argument("--domain", required=True, help="Domain namespace (e.g., defense, corporate)")
    p_intercept.add_argument("--classification", required=True, help="Classification level (e.g., restricted, open)")
    p_intercept.add_argument("--clearance", type=lambda x: x.lower() == 'true', default=False, help="True/False authorized clearance")
    p_intercept.add_argument("--session-id", default="cli_test_session", help="Session ID for tracking state")
    p_intercept.add_argument("--input", default="{}", help="Raw input JSON string for the tool")
    p_intercept.set_defaults(func=cmd_intercept)

    # Session check command
    p_session = subparsers.add_parser("session", help="Retrieve current session state and history")
    p_session.add_argument("session_id", help="Session ID to query")
    p_session.set_defaults(func=cmd_session)

    # Policies check command
    p_policies = subparsers.add_parser("policies", help="View currently loaded active governance rules")
    p_policies.set_defaults(func=cmd_policies)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
