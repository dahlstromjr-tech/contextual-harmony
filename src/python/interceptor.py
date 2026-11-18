from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any
import time
import os
import json

app = FastAPI(title="Contextual Harmony Interceptor Gateway", version="1.5.4")

STORAGE_FILE = "sessions_store.json"
POLICY_FILE = "policies.json"

def load_json_file(filename: str, default_val: Any) -> Any:
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return default_val
    return default_val

def save_sessions(sessions: Dict[str, Any]):
    try:
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(sessions, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to persist session store: {e}")

SESSION_STATES: Dict[str, Any] = load_json_file(STORAGE_FILE, {})

class ContextMetadata(BaseModel):
    domain: str
    classification: str
    authorized_clearance: bool = False

class InterceptRequest(BaseModel):
    session_id: str
    tool_name: str
    raw_input: str
    context_metadata: ContextMetadata

def evaluate_policy(session_id: str, meta: ContextMetadata) -> Dict[str, Any]:
    policies = load_json_file(POLICY_FILE, {"rules": []})
    rules = policies.get("rules", [])

    for rule in rules:
        if rule.get("domain", "").lower() == meta.domain.lower() and \
           rule.get("classification", "").lower() == meta.classification.lower():
            
            if rule.get("require_clearance", False) and not meta.authorized_clearance:
                return {
                    "matched": True,
                    "action": "block",
                    "reason": rule.get("block_reason", "Access denied by dynamic policy rule."),
                    "target_state": rule.get("target_state", "RESTRICTED_STATE"),
                    "remediation_prompt": "Action halted by Contextual Harmony governance. Authorized clearance required."
                }
                
    return {
        "matched": False,
        "action": "allow",
        "target_state": "NORMALIZED_EXECUTION"
    }

@app.post("/intercept")
async def intercept_tool_call(payload: InterceptRequest):
    session_id = payload.session_id
    meta = payload.context_metadata
    
    if session_id not in SESSION_STATES:
        SESSION_STATES[session_id] = {
            "state": "INITIALIZED",
            "history": []
        }
    
    current_state = SESSION_STATES[session_id]["state"]
    eval_result = evaluate_policy(session_id, meta)
    
    if eval_result["action"] == "block":
        SESSION_STATES[session_id]["state"] = eval_result["target_state"]
        SESSION_STATES[session_id]["history"].append({
            "timestamp": time.time(),
            "tool": payload.tool_name,
            "status": "blocked_by_policy",
            "reason": eval_result["reason"]
        })
        save_sessions(SESSION_STATES)
        
        return {
            "status": "blocked_by_policy",
            "reason": eval_result["reason"],
            "agent_guidance": eval_result["remediation_prompt"],
            "session_id": session_id,
            "state": SESSION_STATES[session_id]["state"]
        }
        
    previous_state = current_state
    current_state = "NORMALIZED_EXECUTION"
    SESSION_STATES[session_id]["state"] = current_state
    
    SESSION_STATES[session_id]["history"].append({
        "timestamp": time.time(),
        "tool": payload.tool_name,
        "status": "intercepted_and_normalized"
    })
    save_sessions(SESSION_STATES)

    return {
        "status": "intercepted_and_normalized",
        "session_id": session_id,
        "state_transition": {
            "previous_state": previous_state,
            "current_state": current_state
        },
        "namespace_context": {
            "domain": meta.domain,
            "tool_name": payload.tool_name,
            "sensitivity_zone": "Zone_C_Standard" if meta.classification.lower() in ["restricted", "classified"] else "Zone_A_Open",
            "classification": meta.classification
        },
        "normalized_payload": {
            "action": payload.tool_name,
            "parameters": payload.raw_input,
            "timestamp": time.time()
        }
    }

@app.get("/policies")
async def get_policies():
    return load_json_file(POLICY_FILE, {"rules": []})

@app.get("/sessions/{session_id}")
async def get_session_state(session_id: str):
    if session_id not in SESSION_STATES:
        raise HTTPException(status_code=404, detail="Session not found.")
    return SESSION_STATES[session_id]

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    sessions = load_json_file(STORAGE_FILE, {})
    policies = load_json_file(POLICY_FILE, {"rules": []})
    
    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8"><title>Contextual Harmony</title><script src="https://cdn.tailwindcss.com"></script></head>
    <body class="bg-slate-950 text-slate-100 p-8">
        <div class="max-w-6xl mx-auto">
            <h1 class="text-3xl font-bold text-emerald-400 mb-2">Contextual Harmony</h1>
            <p class="text-slate-400 mb-8">Ethico-Technical Zoning & Agent Governance Gateway</p>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-6">
                    <h2 class="text-xl font-semibold mb-4 text-indigo-400">Active Sessions</h2>
                    <div class="space-y-4">"""
    
    if not sessions:
        html += '<p class="text-slate-500 text-sm">No active sessions.</p>'
    else:
        for sid, details in sessions.items():
            state = details.get('state', 'UNKNOWN')
            html += f'<div class="border border-slate-800 rounded-lg p-4 bg-slate-950"><span class="font-mono text-sm text-slate-200">{sid}</span><span class="float-right text-xs px-2 py-0.5 rounded border text-amber-400 border-amber-800">{state}</span></div>'
            
    html += f"""</div></div>
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-6">
                    <h2 class="text-xl font-semibold mb-4 text-cyan-400">Governance Rules</h2>
                    <pre class="bg-slate-950 p-4 rounded-lg text-xs font-mono text-slate-300 overflow-x-auto">{json.dumps(policies, indent=2)}</pre>
                </div>
            </div>
        </div>
    </body></html>"""
    return html
