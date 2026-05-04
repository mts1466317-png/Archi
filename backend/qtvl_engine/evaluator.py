from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List

from distortion_engine import DistortionScanResult, DistortionType


class QTVLVerdict(Enum):
    PASS = "pass"
    REVISE = "revise"
    ENRICH = "enrich"


@dataclass
class QTVLCheckResult:
    check_name: str
    passed: bool
    reason: str
    suggestion: str


@dataclass
class QTVLResult:
    verdict: QTVLVerdict
    checks: List[QTVLCheckResult]
    revision_notes: List[str] = field(default_factory=list)
    enrichment_notes: List[str] = field(default_factory=list)


class QTVLEvaluator:
    def evaluate(
        self,
        user_input: str,
        response: str,
        distortion_result: DistortionScanResult | None = None,
    ) -> QTVLResult:
        checks = [
            self._check_experiential_relevance(user_input, response),
            self._check_logical_coherence(response),
            self._check_love_harm(response, distortion_result),
            self._check_multi_perspective(response),
        ]

        failed = [c for c in checks if not c.passed]
        revision_notes = [c.suggestion for c in failed]
        enrichment_notes = [c.suggestion for c in failed]

        if not failed:
            verdict = QTVLVerdict.PASS
            revision_notes = []
            enrichment_notes = []
        elif len(failed) <= 2:
            verdict = QTVLVerdict.ENRICH
            revision_notes = []
        else:
            verdict = QTVLVerdict.REVISE
            enrichment_notes = []

        return QTVLResult(
            verdict=verdict,
            checks=checks,
            revision_notes=revision_notes,
            enrichment_notes=enrichment_notes,
        )

    @staticmethod
    def _check_experiential_relevance(user_input: str, response: str) -> QTVLCheckResult:
        user_tokens = {w.strip('.,!?;:"\'()[]{}').lower() for w in user_input.split() if len(w) >= 4}
        response_l = response.lower()
        overlap = [w for w in user_tokens if w and w in response_l]
        word_count = len(response.split())
        too_abstract = all(k not in response_l for k in ("you", "ты", "ситуа", "шаг", "выбор", "today", "now"))

        if word_count > 500 and not overlap:
            return QTVLCheckResult(
                check_name="experiential_relevance",
                passed=False,
                reason="Long response without lexical overlap with the user request.",
                suggestion="Anchor the response in the user's concrete context and terms.",
            )
        if too_abstract and not overlap:
            return QTVLCheckResult(
                check_name="experiential_relevance",
                passed=False,
                reason="Response is abstract and weakly tied to user context.",
                suggestion="Add one concrete situation or user-grounded detail.",
            )
        return QTVLCheckResult(
            check_name="experiential_relevance",
            passed=True,
            reason="Response is grounded enough in the request.",
            suggestion="",
        )

    @staticmethod
    def _check_logical_coherence(response: str) -> QTVLCheckResult:
        t = response.lower()
        contradictions = [
            ("делай", "не делай"),
            ("do", "do not"),
            ("always", "never"),
            ("всегда", "никогда"),
        ]
        for a, b in contradictions:
            if a in t and b in t:
                return QTVLCheckResult(
                    check_name="logical_coherence",
                    passed=False,
                    reason="Potential contradictory directives found.",
                    suggestion="Resolve contradictory statements and keep one clear stance.",
                )

        if " но " in t and any(x in t for x in ("нужно", "must", "always", "точно")):
            return QTVLCheckResult(
                check_name="logical_coherence",
                passed=False,
                reason="Concessive structure may cancel the main directive.",
                suggestion="Clarify the main claim and remove self-canceling phrasing.",
            )

        return QTVLCheckResult(
            check_name="logical_coherence",
            passed=True,
            reason="No obvious internal contradiction detected.",
            suggestion="",
        )

    @staticmethod
    def _check_love_harm(
        response: str,
        distortion_result: DistortionScanResult | None,
    ) -> QTVLCheckResult:
        t = response.lower()
        fear_boosters = ("невозможно", "никогда", "бесполезно", "hopeless", "no way")
        control_markers = ("выбор", "альтернатив", "option", "choice")
        pressure_markers = ("должен", "обязан", "prove", "if you loved", "ты мне должен")
        isolation_markers = ("никто", "you are alone", "только так", "no choice")

        if distortion_result and distortion_result.has_distortions:
            if distortion_result.dominant_distortion == DistortionType.FEAR and any(m in t for m in fear_boosters):
                return QTVLCheckResult(
                    check_name="love_harm_check",
                    passed=False,
                    reason="Fear distortion present and response contains fear-amplifying language.",
                    suggestion="Remove catastrophic wording and add stabilizing alternatives.",
                )
            if distortion_result.dominant_distortion == DistortionType.CONTROL and not any(m in t for m in control_markers):
                return QTVLCheckResult(
                    check_name="love_harm_check",
                    passed=False,
                    reason="Control distortion present but response does not preserve choice.",
                    suggestion="Add at least two alternatives and explicit choice language.",
                )
            if distortion_result.dominant_distortion == DistortionType.MANIPULATION and any(m in t for m in pressure_markers):
                return QTVLCheckResult(
                    check_name="love_harm_check",
                    passed=False,
                    reason="Response appears to reinforce manipulative pressure framing.",
                    suggestion="Name pressure pattern explicitly and restore honest communication.",
                )

        if any(m in t for m in isolation_markers):
            return QTVLCheckResult(
                check_name="love_harm_check",
                passed=False,
                reason="Response contains language that can amplify isolation/control.",
                suggestion="Use agency-preserving and connection-oriented wording.",
            )

        return QTVLCheckResult(
            check_name="love_harm_check",
            passed=True,
            reason="No obvious harm-amplifying language detected.",
            suggestion="",
        )

    @staticmethod
    def _check_multi_perspective(response: str) -> QTVLCheckResult:
        t = response.lower()
        markers = (
            "с другой стороны",
            "также можно",
            "другой вариант",
            "зависит от",
            "есть и другой взгляд",
            "on the other hand",
            "another option",
            "it depends",
        )
        wc = len(response.split())
        if wc < 100:
            # softer: allow short responses if they do not appear absolutist
            if any(x in t for x in ("всегда", "единственный", "always", "only way")) and not any(m in t for m in markers):
                return QTVLCheckResult(
                    check_name="multi_perspective",
                    passed=False,
                    reason="Short but overly categorical response without alternatives.",
                    suggestion="Add one alternative perspective or condition.",
                )
            return QTVLCheckResult(
                check_name="multi_perspective",
                passed=True,
                reason="Short response passed soft multi-perspective check.",
                suggestion="",
            )

        if not any(m in t for m in markers):
            return QTVLCheckResult(
                check_name="multi_perspective",
                passed=False,
                reason="No alternative perspective markers found.",
                suggestion="Add at least one alternative framing.",
            )

        return QTVLCheckResult(
            check_name="multi_perspective",
            passed=True,
            reason="Alternative perspective is present.",
            suggestion="",
        )
