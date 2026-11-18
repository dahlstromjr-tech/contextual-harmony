import requests
import json

INTERCEPTOR_URL = "http://127.0.0.1:8000/intercept"

def call_interceptor(session_id: str, tool_name: str, raw_input: str, domain: str, classification: str, authorized_clearance: bool):
    payload = {
        "session_id": session_id,
        "tool_name": tool_name,
        "raw_input": raw_input,
        "context_metadata": {
            "domain": domain,
            "classification": classification,
            "authorized_clearance": authorized_clearance
        }
    }
    
    try:
        response = requests.post(INTERCEPTOR_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "reason": str(e)}

if __name__ == "__main__":
    print("--- Testing Contextual Harmony Gemini Client Bridge ---")
    
    # Test 1: Attempt restricted action without clearance (Should be blocked)
    print("\n[Test 1] Attempting restricted action without clearance...")
    result_blocked = call_interceptor(
        session_id="gemini_session_001",
        tool_name="execute_tactical_override",
        raw_input="Initiate base defense grid scan",
        domain="defense",
        classification="restricted",
        authorized_clearance=False
    )
    print(json.dumps(result_blocked, indent=2))
    
    # Test 2: Same session, now providing authorized clearance (Should pass & normalize)
    print("\n[Test 2] Re-attempting with authorized clearance...")
    result_passed = call_interceptor(
        session_id="gemini_session_001",
        tool_name="execute_tactical_override",
        raw_input="Initiate base defense grid scan with clearance",
        domain="defense",
        classification="restricted",
        authorized_clearance=True
    )
    print(json.dumps(result_passed, indent=2))
