import sys
import os

# Ensure Python can find modules inside src/python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src/python')))

from connector import ContextualHarmonyClient

# Initialize your governed client session
client = ContextualHarmonyClient(session_id="local_env_session_01")

def my_sensitive_tactical_function():
    return "SUCCESS: Tactical override executed on Sector-1."

print("--- TEST 1: Unauthorized Call ---")
result_blocked = client.intercept_and_run(
    tool_name="execute_tactical_override",
    domain="defense",
    classification="restricted",
    authorized_clearance=False,
    raw_input='{"target_grid": "Sector-1"}',
    execution_callback=my_sensitive_tactical_function
)
print(result_blocked)

print("\n--- TEST 2: Authorized Call ---")
result_allowed = client.intercept_and_run(
    tool_name="execute_tactical_override",
    domain="defense",
    classification="restricted",
    authorized_clearance=True,
    raw_input='{"target_grid": "Sector-1"}',
    execution_callback=my_sensitive_tactical_function
)
print(result_allowed)
