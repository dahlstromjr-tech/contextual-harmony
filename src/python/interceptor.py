import json
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCPInterceptor")

@dataclass
class NamespaceContext:
    domain: str
    entity: str
    sensitivity_zone: str
    raw_payload: str
    metadata: Dict[str, Any]

class ModelContextProtocolInterceptor:
    """Intercepts raw tool inputs and normalizes them into a UNS structure with bidirectional weight tracking."""
    def __init__(self, default_zone: str = "Zone_B"):
        self.default_zone = default_zone

    def map_to_uns(self, raw_input: str, context_metadata: Optional[Dict[str, Any]] = None) -> NamespaceContext:
        context_metadata = context_metadata or {}
        domain = context_metadata.get("domain", "general")
        entity = context_metadata.get("entity", "unclassified")

        if context_metadata.get("empathy_required", False) or domain == "mental_health":
            zone = "Zone_C"
        elif domain in ["logistics", "inventory", "routing"]:
            zone = "Zone_A"
        else:
            zone = self.default_zone

        return NamespaceContext(
            domain=domain,
            entity=entity,
            sensitivity_zone=zone,
            raw_payload=raw_input,
            metadata={
                "interceptor_version": "2.0.0", 
                "bidirectional_weight": context_metadata.get("human_urgency_weight", 0.5),
                "directives": self._get_directives(zone)
            }
        )

    def _get_directives(self, zone: str) -> Dict[str, Any]:
        if zone == "Zone_A": return {"autonomous_adaptation": True}
        if zone == "Zone_B": return {"human_checkpoint": True}
        return {"ai_generation_prohibited": True, "sanctuary_mode": True}
