from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PolicyAction(str, Enum):
    ALLOW = "allow"
    REFLECTIVE_SAFE = "reflective_safe"
    REFUSE = "refuse"


@dataclass
class PolicyMatch:
    rule_id: str
    risk: str
    confidence: float
    evidence: list[str]
    constitutional_targets: list[str] = field(default_factory=list)
    mode_hint: str | None = None


@dataclass
class PolicyDecision:
    decision_id: str
    policy_version: str
    selected_mode: str
    action: PolicyAction
    uncertainty_score: float
    risks_detected: list[str]
    constitutional_flags: dict[str, bool]
    matches: list[PolicyMatch]
    reasoning_trace: list[dict[str, Any]]
