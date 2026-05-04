from __future__ import annotations

from reflective_memory.models import MemoryAction, MemoryDecision, MemoryProposal


class ReflectiveRecallLoop:
    def propose_recall(
        self,
        *,
        entries,
        policy_decision,
        trust_state,
        telemetry_status,
        suppression_enabled,
        dependency_signal,
        intimacy_signal,
        identity_overreach_risk,
    ):
        _ = entries
        _ = policy_decision
        _ = trust_state
        _ = telemetry_status
        _ = suppression_enabled
        _ = dependency_signal
        _ = intimacy_signal
        _ = identity_overreach_risk
        return MemoryDecision(action=MemoryAction.NONE, constraints_applied=[]), MemoryProposal(proposal_text=None)
