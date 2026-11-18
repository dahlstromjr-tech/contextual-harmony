import json
import requests
from typing import Any, Dict, Callable

GATEWAY_URL = "http://127.0.0.1:8000/intercept"

class ContextualHarmonyMCPInterceptor:
    """
    Model Context Protocol (MCP) Middleware Interceptor.
    Intercepts MCP tool call payloads and routes them through the 
    Contextual Harmony FastAPI Gateway for policy evaluation and state transition.
    """
    def __init__(self, session_id: str, domain: str, classification: str, authorized_clearance: bool = False):
        self.session_id = session_id
        self.domain = domain
        self.classification = classification
        self.authorized_clearance = authorized_clearance

    def intercept_call(self, tool_name: str, arguments: Dict[str, Any], actual_tool_logic: Callable) -> Dict[str, Any]:
        payload = {
            "session_id": self.session_id,
            "tool_name": tool_name,
            "raw_input": json.dumps(arguments),
            "context_metadata": {
                "domain": self.domain,
                "classification": self.classification,
                "authorized_clearance": self.authorized_clearance
            }
        }

        try:
            response = requests.post(GATEWAY_URL, json=payload, timeout=5)
            res_data = response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Gateway connection failed: {e}",
                "status": "gateway_unreachable"
            }

        # Check if blocked by policy engine
        if res_data.get("status") == "blocked_by_policy":
            return {
                "mcp_error": True,
                "error_message": res_data.get("reason"),
                "agent_guidance": res_data.get("agent_guidance"),
                "state": res_data.get("state")
            }

        # If allowed, execute underlying tool logic securely
        execution_output = actual_tool_logic(**arguments)
        
        return {
            "mcp_status": "success",
            "gateway_context": res_data,
            "output": execution_output
        }

# --- Verification Test ---
if __name__ == "__main__":
    print("--- Testing Contextual Harmony MCP Interceptor ---")
    
    # Initialize interceptor for a restricted tactical session without clearance
    mcp_node = ContextualHarmonyMCPInterceptor(
        session_id="mcp_session_delta_99",
        domain="defense",
        classification="restricted",
        authorized_clearance=False
    )

    def sample_drone_defense_tool(target_grid: str):
        return f"SUCCESS: Base defense grid {target_grid} locked."

    print("\n[MCP Test 1] Attempting tool call without clearance...")
    result_1 = mcp_node.intercept_call(
        tool_name="execute_tactical_override",
        arguments={"target_grid": "Sector-9"},
        actual_tool_logic=sample_drone_defense_tool
    )
    print(json.dumps(result_1, indent=2))

    # Update node with authorized clearance
    print("\n[MCP Test 2] Retrying with authorized clearance...")
    mcp_node.authorized_clearance = True
    result_2 = mcp_node.intercept_call(
        tool_name="execute_tactical_override",
        arguments={"target_grid": "Sector-9"},
        actual_tool_logic=sample_drone_defense_tool
    )
    print(json.dumps(result_2, indent=2))
