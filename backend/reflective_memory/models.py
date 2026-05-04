from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


@dataclass
class ReflectionMemoryEntry:
    entry_id: str
    entry_type: str
    content: str
    source_context_id: str
    user_confirmed: bool
    confidence_provenance: dict[str, str] = field(default_factory=dict)
    created_at: str = ""
    expires_at: str = ""
    motif_frame: str = "default"


class MemoryAction(str, Enum):
    NONE = "none"


@dataclass
class MemoryDecision:
    action: MemoryAction
    constraints_applied: list[str]


@dataclass
class MemoryProposal:
    proposal_text: str | None = None
