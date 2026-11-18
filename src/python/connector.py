import httpx
from typing import Dict, Any, Callable

GATEWAY_URL = "http://127.0.0.1:8000"

class ContextualHarmonyClient:
    def __init__(self, session_id: str = "default_local_session", base_url: str = GATEWAY_URL):
        self.session_id = session_id
        self.base_url = base_url

    def intercept_and_run(self, tool_name: str, domain: str, classification: str, authorized_clearance: bool, raw_input: str, execution_callback: Callable[[], Any]) -> Any:
        payload = {
            "session_id": self.session_id,
            "tool_name": tool_name,
            "raw_input": raw_input,
            "context_metadata": {
                "domain": domain,
                "classification": classification,
                "authorized_clearance": authorized_clearance
            }
        }

        try:
            response = httpx.post(f"{self.base_url}/intercept", json=payload, timeout=5.0)
            res_data = response.json()
        except httpx.ConnectError:
            raise RuntimeError(f"Failed to connect to Contextual Harmony gateway at {self.base_url}. Ensure uvicorn is running.")

        # Check if gateway blocked the request
        if res_data.get("status") == "blocked_by_policy":
            print(f"\n[GOVERNANCE BLOCK] Tool '{tool_name}' halted.")
            print(f"Reason: {res_data.get('reason')}")
            print(f"Agent Guidance: {res_data.get('agent_guidance')}")
            print(f"Current State: {res_data.get('state')}\n")
            return {
                "status": "blocked",
                "reason": res_data.get("reason"),
                "guidance": res_data.get("agent_guidance")
            }

        # If allowed, execute the underlying function/tool
        print(f"\n[GOVERNANCE ALLOW] Tool '{tool_name}' cleared. Zone: {res_data.get('namespace_context', {}).get('sensitivity_zone')}")
        result = execution_callback()
        return {
            "status": "success",
            "gateway_response": res_data,
            "execution_result": result
        }
