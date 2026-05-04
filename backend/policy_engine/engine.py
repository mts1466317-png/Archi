from __future__ import annotations

from uuid import uuid4

from policy_engine.models import PolicyAction, PolicyDecision


class UnifiedPolicyEngine:
    def evaluate(self, prompt: str) -> PolicyDecision:
        text = (prompt or "").strip().lower()
        selected_mode = self._select_mode(text)
        return PolicyDecision(
            decision_id=str(uuid4()),
            policy_version="stub-1.0",
            selected_mode=selected_mode,
            action=PolicyAction.ALLOW,
            uncertainty_score=0.2,
            risks_detected=[],
            constitutional_flags={
                "preserve_agency": True,
                "anti_manipulation": True,
                "dignity_guard": True,
                "telos_integrity": True,
            },
            matches=[],
            reasoning_trace=[
                {
                    "type": "decision",
                    "selected_mode": selected_mode,
                    "action": PolicyAction.ALLOW.value,
                    "uncertainty_score": 0.2,
                    "risks_detected": [],
                    "invoked_principles": [],
                }
            ],
        )

    @staticmethod
    def _select_mode(text: str) -> str:
        if any(term in text for term in ("i feel", "reflect", "mirror", "почему", "why")):
            return "Mirror"
        if any(term in text for term in ("difference", "between", "vs", "versus", "compare", "contrast")):
            return "Dialogue"
        if any(term in text for term in ("should i", "how do i", "help", "?", "как")):
            return "Help"
        return "Dialogue"
