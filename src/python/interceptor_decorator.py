import functools
import requests
import json

INTERCEPTOR_URL = "http://127.0.0.1:8000/intercept"

def intercept_tool(domain: str, classification: str):
    """
    A decorator that routes tool calls through the Contextual Harmony Interceptor Gateway
    before executing the underlying function.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract governance metadata from kwargs, providing safe defaults
            session_id = kwargs.get("session_id", "session_alpha_001")
            authorized_clearance = kwargs.get("authorized_clearance", False)
            raw_input = kwargs.get("raw_input", f"Executing {func.__name__}")
            
            payload = {
                "session_id": session_id,
                "tool_name": func.__name__,
                "raw_input": raw_input,
                "context_metadata": {
                    "domain": domain,
                    "classification": classification,
                    "authorized_clearance": authorized_clearance
                }
            }
            
            print(f"\n[INTERCEPTOR GATEWAY] Intercepting tool: '{func.__name__}' [Zone: {classification.upper()}]")
            try:
                response = requests.post(INTERCEPTOR_URL, json=payload)
                response.raise_for_status()
                res_data = response.json()
            except requests.exceptions.RequestException as e:
                return {"status": "error", "reason": f"Gateway connection failed: {str(e)}"}
            
            # Evaluate gateway response
            if res_data.get("status") == "blocked_by_policy":
                print(f"❌ Policy Blocked: {res_data.get('reason')}")
                print(f"   State Machine: {res_data.get('state')}")
                return res_data
            
            print(f"✅ Policy Cleared: Transitioned to {res_data.get('state_transition', {}).get('current_state')}")
            
            # Filter out interceptor metadata kwargs before running the underlying tool
            clean_kwargs = {k: v for k, v in kwargs.items() if k not in ["session_id", "authorized_clearance", "raw_input"]}
            
            # Execute actual underlying tool logic
            execution_output = func(*args, **clean_kwargs)
            
            return {
                "gateway_context": res_data,
                "output": execution_output
            }
        return wrapper
    return decorator

# --- Verification Test ---
if __name__ == "__main__":
    print("--- Testing Contextual Harmony @intercept_tool Decorator ---")
    
    # Define a mock tactical tool function wrapped with our decorator
    @intercept_tool(domain="defense", classification="restricted")
    def execute_tactical_override(target_grid: str):
        return f"SUCCESS: Perimeter scan completed on grid {target_grid}."

    # Test Turn 1: Without Clearance (Should be blocked by gateway)
    print("\n[Turn 1] Calling tool WITHOUT clearance...")
    result_1 = execute_tactical_override(target_grid="Sector-7", authorized_clearance=False)
    print(json.dumps(result_1, indent=2))

    # Test Turn 2: With Clearance (Should pass gateway & execute tool)
    print("\n[Turn 2] Calling tool WITH authorized clearance...")
    result_2 = execute_tactical_override(target_grid="Sector-7", authorized_clearance=True)
    print(json.dumps(result_2, indent=2))
