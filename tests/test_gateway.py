import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/python')))
from interceptor import app

client = TestClient(app)

def test_health_and_policies():
    response = client.get("/policies")
    assert response.status_code == 200
    data = response.json()
    assert "rules" in data

def test_unauthorized_restricted_call_blocked():
    payload = {
        "session_id": "test_session_block_fresh",
        "tool_name": "execute_tactical_override",
        "raw_input": '{"target_grid": "Sector-1"}',
        "context_metadata": {
            "domain": "defense",
            "classification": "restricted",
            "authorized_clearance": False
        }
    }
    response = client.post("/intercept", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "blocked_by_policy"
    assert res_data["state"] == "RESTRICTED_STATE"

def test_authorized_restricted_call_allowed():
    payload = {
        "session_id": "test_session_allow_fresh",
        "tool_name": "execute_tactical_override",
        "raw_input": '{"target_grid": "Sector-1"}',
        "context_metadata": {
            "domain": "defense",
            "classification": "restricted",
            "authorized_clearance": True
        }
    }
    response = client.post("/intercept", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "intercepted_and_normalized"
