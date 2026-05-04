from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TrustStateName(str, Enum):
    TENTATIVE_TRUST = "tentative_trust"


class TrustAction(str, Enum):
    HOLD = "hold"


@dataclass
class TrustState:
    state: TrustStateName
    score: float
    confidence: float
    policy_version: str
    hazard_flags: dict[str, bool] = field(default_factory=dict)
    updated_at: str = ""


@dataclass
class TrustAdjustment:
    action: TrustAction
    constraints_applied: list[str]


@dataclass
class TrustEvent:
    trace_link: str
