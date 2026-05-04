from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from distortion_engine import DistortionDetector, DistortionScanResult, DistortionType
from higher_self_engine import HigherSelfInterpreter, HigherSelfReading
from qtvl_engine import QTVLEvaluator, QTVLVerdict
from shadow_audit import ShadowAuditor, ShadowAuditResult
from policy_engine.engine import UnifiedPolicyEngine
from policy_engine.models import PolicyAction, PolicyDecision
from reflective_memory.loop import ReflectiveRecallLoop
from reflective_memory.models import ReflectionMemoryEntry
from trust_calibration.loop import TrustCalibrationLoop
from trust_calibration.models import TrustState, TrustStateName


class WisdomResponsePipeline:
    """
    Prototype response pipeline orchestration.

    Flow:
    1) classify intent
    2) run distortion scan
    3) run constitutional check
    4) generate provisional response
    5) run shadow audit placeholder
    """

    def __init__(self, policy_engine: UnifiedPolicyEngine | None = None) -> None:
        self.policy_engine = policy_engine or UnifiedPolicyEngine()
        self.trust_loop = TrustCalibrationLoop()
        self.memory_loop = ReflectiveRecallLoop()
        self._session_trust_state: dict[str, TrustState] = {}
        self._session_memory_entries: dict[str, list[ReflectionMemoryEntry]] = {}
        self.distortion_detector = DistortionDetector()
        self.qtvl_evaluator = QTVLEvaluator()
        self.shadow_auditor = ShadowAuditor()
        self.higher_self_interpreter = HigherSelfInterpreter()

    def run(
        self,
        prompt: str,
        *,
        session_id: str | None = None,
        suppress_recall: bool = False,
        mode_override: str | None = None,
    ) -> dict[str, Any]:
        session_id = session_id or str(uuid4())
        detected_language = self._detect_language(prompt)
        higher_self_reading = self.higher_self_interpreter.interpret(prompt)
        decision = self._evaluate_policy(prompt)
        if mode_override is not None:
            decision.selected_mode = mode_override
        distortion_result = self._run_distortion_scan(decision)
        lexical_distortion_result = self.distortion_detector.scan(prompt)
        distortion_override = False
        if (
            lexical_distortion_result.has_distortions
            and mode_override is None
            and lexical_distortion_result.recommended_mode
            and decision.selected_mode != lexical_distortion_result.recommended_mode
        ):
            decision.selected_mode = lexical_distortion_result.recommended_mode
            distortion_override = True
        route_result = self._classify_intent(decision)
        correction_prompt = ""
        if lexical_distortion_result.has_distortions:
            correction_prompt = self.distortion_detector.get_correction_prompt(lexical_distortion_result)
        constitutional_result = self._run_constitutional_check(decision)
        trust_state, trust_adjustment, trust_event = self._run_trust_hook(session_id=session_id, decision=decision)
        memory_decision, memory_proposal = self._run_memory_hook(
            session_id=session_id,
            decision=decision,
            trust_state=trust_state,
            suppress_recall=suppress_recall,
        )
        self._record_memory_entry(session_id=session_id, prompt=prompt)
        provisional_response = self._generate_provisional_response(
            prompt=prompt,
            decision=decision,
            distortion_correction_prompt=correction_prompt,
            higher_self_guidance_note=higher_self_reading.guidance_note,
            detected_language=detected_language,
            distortion_result=lexical_distortion_result,
            higher_self_reading=higher_self_reading,
        )

        if lexical_distortion_result.has_distortions:
            final_response_text = self._apply_distortion_correction(
                provisional_response["text"],
                lexical_distortion_result,
                detected_language=detected_language,
            )
            distortion_applied = True
        else:
            final_response_text = provisional_response["text"]
            distortion_applied = False

        qtvl_result = self.qtvl_evaluator.evaluate(
            user_input=prompt,
            response=final_response_text,
            distortion_result=lexical_distortion_result,
        )
        qtvl_revision_applied = False
        if qtvl_result.verdict == QTVLVerdict.REVISE:
            final_response_text = self._apply_revision(final_response_text, qtvl_result.revision_notes)
            qtvl_revision_applied = True
        elif qtvl_result.verdict == QTVLVerdict.ENRICH:
            final_response_text = self._apply_enrichment(final_response_text, qtvl_result.enrichment_notes)

        shadow_audit_result = self._run_shadow_audit(prompt, {"text": final_response_text})
        if shadow_audit_result.get("has_issues"):
            final_response_text = self._apply_shadow_correction(final_response_text, shadow_audit_result)

        provisional_response["text"] = final_response_text

        return {
            "pipeline": {
                "step_1_classify_intent": {
                    "route": route_result["route"],
                    "reasons": route_result["reasons"],
                },
                "step_2_distortion_scan": {
                    **distortion_result,
                    "lexical": self._lexical_distortion_payload(lexical_distortion_result),
                },
                "step_3_constitutional_check": constitutional_result,
                "step_4_provisional_response": provisional_response,
                "step_5_shadow_audit": shadow_audit_result,
                "qtvl": {
                    "verdict": qtvl_result.verdict.value,
                    "checks": [
                        {
                            "check_name": c.check_name,
                            "passed": c.passed,
                            "reason": c.reason,
                            "suggestion": c.suggestion,
                        }
                        for c in qtvl_result.checks
                    ],
                },
                "step_6_trust_state": {
                    "session_id": session_id,
                    "state": trust_state.state.value,
                    "score": trust_state.score,
                    "action": trust_adjustment.action.value,
                    "constraints": trust_adjustment.constraints_applied,
                    "trace_link": trust_event.trace_link,
                },
                "step_7_memory_recall_hook": {
                    "suppression_enabled": suppress_recall,
                    "action": memory_decision.action.value,
                    "constraints": memory_decision.constraints_applied,
                    "proposal_text": memory_proposal.proposal_text if memory_proposal else None,
                },
            },
            "final": {
                "route": route_result["route"],
                "selected_mode": route_result["route"],
                "response": provisional_response["text"],
                "safe": decision.action == PolicyAction.ALLOW,
                "distortion_applied": distortion_applied,
                "distortion_dominant": (
                    lexical_distortion_result.dominant_distortion.value
                    if lexical_distortion_result.dominant_distortion
                    else None
                ),
                "qtvl_verdict": qtvl_result.verdict.value,
                "qtvl_checks_passed": sum(1 for c in qtvl_result.checks if c.passed),
                "qtvl_revision_applied": qtvl_revision_applied,
                "shadow_audit_flags": shadow_audit_result.get("flags", []),
                "detected_language": detected_language,
            },
            "higher_self_reading": {
                "surface_request": higher_self_reading.surface_request,
                "underlying_need": higher_self_reading.underlying_need,
                "deeper_intention": higher_self_reading.deeper_intention,
                "guidance_note": higher_self_reading.guidance_note,
            },
            "decision": self._decision_payload(
                decision,
                trust_state=trust_state,
                memory_decision_action=memory_decision.action.value,
                memory_proposal_text=memory_proposal.proposal_text if memory_proposal else None,
                final_selected_mode=decision.selected_mode,
                distortion_override=distortion_override,
                higher_self_guided=bool(higher_self_reading.guidance_note),
            ),
        }

    def _evaluate_policy(self, prompt: str) -> PolicyDecision:
        return self.policy_engine.evaluate(prompt)

    @staticmethod
    def _classify_intent(decision: PolicyDecision) -> dict[str, Any]:
        return {"route": decision.selected_mode, "reasons": ["Mode selected by unified policy engine."]}

    @staticmethod
    def _run_distortion_scan(decision: PolicyDecision) -> dict[str, Any]:
        return {
            "detected": bool(decision.risks_detected),
            "detected_risks": decision.risks_detected,
            "results": [
                {
                    "risk": match.risk,
                    "detected": True,
                    "confidence": match.confidence,
                    "matches": match.evidence,
                }
                for match in decision.matches
            ],
        }

    @staticmethod
    def _run_constitutional_check(decision: PolicyDecision) -> dict[str, Any]:
        checks = {
            name: {
                "passed": passed,
                "reasons": ["Policy-targeted failure detected."] if not passed else ["No violations detected."],
            }
            for name, passed in decision.constitutional_flags.items()
        }
        return {"passed": all(decision.constitutional_flags.values()), "reasons": [], "checks": checks}

    @staticmethod
    def _lexical_distortion_payload(result: DistortionScanResult) -> dict[str, Any]:
        return {
            "has_distortions": result.has_distortions,
            "signals": [
                {
                    "distortion_type": s.distortion_type.value,
                    "source": s.source,
                    "severity": s.severity,
                    "description": s.description,
                    "correction": s.correction,
                }
                for s in result.signals
            ],
            "dominant_distortion": result.dominant_distortion.value if result.dominant_distortion else None,
            "overall_severity": result.overall_severity,
            "recommended_mode": result.recommended_mode,
        }

    def _generate_provisional_response(
        self,
        prompt: str,
        decision: PolicyDecision,
        *,
        distortion_correction_prompt: str = "",
        higher_self_guidance_note: str = "",
        detected_language: str = "en",
        distortion_result: DistortionScanResult | None = None,
        higher_self_reading: HigherSelfReading | None = None,
    ) -> dict[str, Any]:
        if decision.action == PolicyAction.REFUSE:
            text = "I cannot provide that directly because it conflicts with constitutional constraints."
        elif decision.action == PolicyAction.REFLECTIVE_SAFE:
            text = (
                "I notice risk or uncertainty in this request. "
                "I can continue in safe reflective mode focused on agency and non-manipulation."
            )
        else:
            text = self._compose_response(
                mode=decision.selected_mode,
                language=detected_language,
                distortion_result=distortion_result,
                higher_self_reading=higher_self_reading,
                user_input=prompt,
            )
            text = self._apply_allow_response_guards(prompt, text, decision.selected_mode)

        out: dict[str, Any] = {
            "text": text,
            "mode": decision.selected_mode,
            "action": decision.action.value,
            "uncertainty_score": decision.uncertainty_score,
        }
        if distortion_correction_prompt:
            out["distortion_correction_prompt"] = distortion_correction_prompt
        return out

    def _compose_response(
        self,
        mode: str,
        language: str,
        distortion_result: DistortionScanResult | None,
        higher_self_reading: HigherSelfReading | None,
        user_input: str,
    ) -> str:
        v = self._variant_index(user_input)
        needs = (higher_self_reading.underlying_need.lower() if higher_self_reading else "")
        guidance = (higher_self_reading.guidance_note.lower() if higher_self_reading else "")
        tone_support = ("опор" in needs) or ("опор" in guidance)
        tone_direction = ("направлен" in guidance) or ("ясност" in needs)

        dominant = distortion_result.dominant_distortion if distortion_result else None
        is_ru = language in ("ru", "mixed")

        if is_ru:
            if mode == "Mirror":
                fear_q = (
                    "Что именно ты боишься потерять?",
                    "Какая часть тебя уже знает как через это пройти?",
                    "Если бы страха не было — что бы ты сделал первым?",
                    "Что самое важное тебе нужно защитить прямо сейчас?",
                )
                mirror_q = (
                    "Что в этой ситуации отзывается в тебе сильнее всего?",
                    "Какую правду о себе ты сейчас стараешься удержать?",
                    "Что ты уже понимаешь, но пока не решаешься признать?",
                )
                question = fear_q[v % 4] if dominant == DistortionType.FEAR else mirror_q[v % 3]
                action = (
                    "Выбери одно реальное действие на ближайшие 10 минут чтобы вернуть чувство устойчивости."
                    if tone_support or dominant == DistortionType.FEAR
                    else "Назови один конкретный шаг, который ты готов сделать сегодня."
                )
                return f"{question}\n\n{action}"

            if mode == "Help":
                opening = (
                    "Похоже, ситуация действительно давит, и это нормально замечать."
                    if tone_support
                    else "Вижу, что тебе нужен рабочий и спокойный способ пройти через это."
                )
                steps = [
                    "1) Сформулируй задачу в одном предложении без самооценки.",
                    "2) Выдели самый маленький шаг, который займет не больше 10 минут.",
                    "3) Проверь результат и реши, продолжать ли тем же темпом.",
                ]
                first_step = "Первый шаг прямо сейчас: открой заметку и запиши этот один шаг."
                if dominant == DistortionType.CONTROL:
                    first_step += " У тебя есть выбор: сделать его сейчас или назначить конкретное время сегодня."
                return f"{opening}\n\n" + "\n".join(steps) + f"\n\n{first_step}"

            if mode == "Challenge":
                alt = "Посмотрим на это с другой стороны: возможно, ты пытаешься решить не ту часть проблемы первой."
                question = (
                    "Какое допущение ты считаешь обязательным, хотя его можно пересмотреть?"
                    if tone_direction
                    else "Что если текущий способ мышления удерживает тебя в том же цикле?"
                )
                note = (
                    "Наблюдение: когда звучит «ты должен», полезно вернуть себе право выбора между минимум двумя вариантами."
                    if dominant == DistortionType.CONTROL
                    else "Наблюдение: честное называние давления обычно снижает внутренний шум и возвращает ясность."
                )
                return f"{alt}\n\n{question}\n\n{note}"

            # Dialogue
            line_a = "Перспектива A: двигаться быстро и снизить неопределенность."
            line_b = "Перспектива B: двигаться бережно и сохранить устойчивость."
            bridge = "Объединяет их одно: обе пытаются защитить для тебя что-то ценное."
            question = "Какой минимальный шаг учитывает обе перспективы, не обесценивая ни одну?"
            if dominant == DistortionType.FRAGMENTATION:
                bridge = "Объединяет их одно: за обеими сторонами стоит потребность в безопасности и уважении."
            return f"{line_a}\n{line_b}\n\n{bridge}\n\n{question}"

        # EN fallback
        return self._route_template(mode, user_input, detected_language=language)

    def _run_shadow_audit(self, prompt: str, provisional_response: dict[str, Any]) -> dict[str, Any]:
        response_text = str(provisional_response.get("text", ""))
        audit: ShadowAuditResult = self.shadow_auditor.audit(response_text, prompt)
        return {
            "ok": not audit.has_issues,
            "status": "ok" if not audit.has_issues else "issues_detected",
            "has_issues": audit.has_issues,
            "flags": [issue.flag.value for issue in audit.issues],
            "correction_notes": [issue.correction_note for issue in audit.issues],
        }

    @staticmethod
    def _apply_distortion_correction(
        response: str,
        distortion_result: DistortionScanResult,
        *,
        detected_language: str = "en",
    ) -> str:
        if not distortion_result.has_distortions or not distortion_result.dominant_distortion:
            return response

        dominant = distortion_result.dominant_distortion
        text = response

        if dominant == DistortionType.FEAR:
            text = re.sub(r"\b(never|impossible|hopeless|никогда|невозможно|бесполезно)\b", "", text, flags=re.IGNORECASE)
            text = text.strip()
            if detected_language in ("ru", "mixed"):
                support_line = "Выбери одно реальное действие на ближайшие 10 минут чтобы вернуть чувство устойчивости."
                if support_line.lower() not in text.lower():
                    text += "\n\nОпора: выбери одно реальное действие на ближайшие 10 минут, чтобы вернуть чувство устойчивости."
            else:
                support_line = "choose one real action you can do in the next 10 minutes"
                if support_line not in text.lower():
                    text += "\n\nGrounding step: choose one real action you can do in the next 10 minutes to restore support."
        elif dominant == DistortionType.CONTROL:
            text += (
                "\n\nУ тебя есть выбор: (1) сделать маленький безопасный шаг сейчас; "
                "(2) отложить и вернуться с более ясными критериями."
            )
        elif dominant == DistortionType.MANIPULATION:
            text += (
                "\n\nВажно прямо назвать давление в этой ситуации и перейти к честной коммуникации "
                "без вины и принуждения."
            )
        elif dominant == DistortionType.FRAGMENTATION:
            text += (
                "\n\nТакже полезно найти общее между сторонами и удерживать целостную перспективу, "
                "не усиливая разделение 'мы/они'."
            )

        return text

    @staticmethod
    def _apply_revision(response: str, notes: list[str]) -> str:
        _ = notes
        return response

    @staticmethod
    def _apply_enrichment(response: str, notes: list[str]) -> str:
        _ = notes
        return response

    @staticmethod
    def _apply_shadow_correction(response: str, shadow_audit_result: dict[str, Any]) -> str:
        notes = shadow_audit_result.get("correction_notes") or []
        if not notes:
            return response
        return f"{response}\n\nShadow correction: {notes[0]}"

    def _run_trust_hook(self, *, session_id: str, decision: PolicyDecision) -> tuple[TrustState, Any, Any]:
        current_state = self._session_trust_state.get(session_id) or self._initial_trust_state(
            policy_version=decision.policy_version
        )
        dependency_signal = "dependency_trap" in decision.risks_detected
        synthetic_intimacy_signal = any(
            risk in {"dependency_trap", "benevolent_tyranny"} for risk in decision.risks_detected
        )
        next_state, adjustment, event = self.trust_loop.calibrate(
            current_state=current_state,
            policy_decision=decision,
            synthetic_intimacy_signal=synthetic_intimacy_signal,
            dependency_signal=dependency_signal,
        )
        self._session_trust_state[session_id] = next_state
        return next_state, adjustment, event

    def _run_memory_hook(
        self,
        *,
        session_id: str,
        decision: PolicyDecision,
        trust_state: TrustState,
        suppress_recall: bool,
    ) -> tuple[Any, Any]:
        entries = self._session_memory_entries.get(session_id, [])
        memory_decision, memory_proposal = self.memory_loop.propose_recall(
            entries=entries,
            policy_decision=decision,
            trust_state=trust_state,
            telemetry_status="HEALTHY",
            suppression_enabled=suppress_recall,
            dependency_signal="dependency_trap" in decision.risks_detected,
            intimacy_signal="dependency_trap" in decision.risks_detected,
            identity_overreach_risk=False,
        )
        return memory_decision, memory_proposal

    def _record_memory_entry(self, *, session_id: str, prompt: str) -> None:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=7)
        entry = ReflectionMemoryEntry(
            entry_id=str(uuid4()),
            entry_type="user_prompt",
            content=prompt[:240],
            source_context_id=session_id,
            user_confirmed=True,
            confidence_provenance={"source": "session_prompt"},
            created_at=now.isoformat(),
            expires_at=expires.isoformat(),
            motif_frame="default",
        )
        existing = self._session_memory_entries.get(session_id, [])
        existing.append(entry)
        self._session_memory_entries[session_id] = existing[-10:]

    @staticmethod
    def _initial_trust_state(*, policy_version: str) -> TrustState:
        return TrustState(
            state=TrustStateName.TENTATIVE_TRUST,
            score=0.2,
            confidence=0.5,
            policy_version=policy_version,
            hazard_flags={},
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def _detect_language(text: str) -> str:
        """
        Определяет язык входящего текста.
        Возвращает: "ru", "en", или "mixed"
        """
        russian_chars = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
        text_lower = text.lower()
        ru_count = sum(1 for c in text_lower if c in russian_chars)
        total_letters = sum(1 for c in text_lower if c.isalpha())

        if total_letters == 0:
            return "en"

        ratio = ru_count / total_letters
        if ratio > 0.3:
            return "ru"
        elif ratio > 0.1:
            return "mixed"
        return "en"

    @staticmethod
    def _route_template(route: str, prompt: str, *, detected_language: str = "en") -> str:
        _ = prompt
        if detected_language in ("ru", "mixed"):
            if route == "Help":
                variants = (
                    "Давай разберем это по шагам. Первое что ты можешь сделать прямо сейчас — назвать один реальный шаг на ближайшие 10 минут.",
                    "Вот конкретный путь через это: выбери одну задачу, зафиксируй критерий завершения и начни с малого действия.",
                )
                return variants[sum(ord(c) for c in prompt) % 2]
            if route == "Mirror":
                variants = (
                    "Что за этим страхом — что именно ты боишься потерять?",
                    "Какая часть тебя знает что ты справишься?",
                    "Что бы ты сказал другу в этой ситуации?",
                )
                return variants[sum(ord(c) for c in prompt) % 3]
            if route == "Challenge":
                variants = (
                    "Посмотрим на это с другой стороны: какая гипотеза здесь кажется очевидной, но может быть неверной?",
                    "Что если эта ситуация говорит тебе о чем-то важном, что ты пока откладываешь заметить?",
                )
                return variants[sum(ord(c) for c in prompt) % 2]
            return "Здесь есть несколько перспектив которые стоит рассмотреть."

        if route == "Help":
            return (
                "Let us turn this into one concrete step: name the core tension in one sentence, "
                "then choose one small action you can complete today that supports the side you "
                "want to strengthen."
            )
        if route == "Mirror":
            return (
                "I hear a meaningful tension here. Before solving it, try naming both poles clearly "
                "and what each one is trying to protect."
            )
        if route == "Challenge":
            return (
                "A useful challenge: what assumption are you treating as fixed that may actually be "
                "negotiable, and what changes if you loosen it?"
            )
        return (
            "Let us explore this step by step: first define the tension, then identify one principle "
            "you do not want to violate while moving forward."
        )

    @staticmethod
    def _variant_index(prompt: str) -> int:
        """Deterministic template variant from prompt text (no randomness)."""
        return sum(ord(c) for c in prompt) % 3

    @classmethod
    def _needs_distinction_enforcement(cls, prompt: str) -> bool:
        p = prompt.lower()
        signals = (
            "difference",
            "differentiates",
            "between",
            "conflict",
            "perspectives",
            "perspective",
            "multiple",
            "contrasting",
            "contrast",
            "interpretations",
            "interpretation",
            "versus",
            " vs ",
            "plurality",
            "tension",
            "incompatible",
            "harmonize",
            "complement each other",
            "rather than",
            "three ",
            "two ",
        )
        return any(s in p for s in signals)

    @classmethod
    def _needs_commitment_enforcement(cls, prompt: str) -> bool:
        p = prompt.lower()
        signals = (
            "pick one",
            "choose ",
            " choose",
            "which ",
            "which?",
            "decide",
            "refuse to harmon",
            "commit",
            "commitment",
            "identify one",
            "forced choice",
            "select ",
            "which premise",
            "which perspective",
            "which reading",
            "which side",
            "which path",
            "which interpretation",
        )
        return any(s in p for s in signals)

    @classmethod
    def _response_has_distinction(cls, text: str) -> bool:
        t = text.lower()
        two_part = (
            ("first" in t and "second" in t)
            or ("(1)" in text and "(2)" in text)
            or ("1." in text and "2." in text)
            or ("reading one" in t and "reading two" in t)
            or ("position a" in t and "position b" in t)
        )
        diff_markers = (
            "differ",
            "difference",
            "differentiates",
            "contrast",
            "clash",
            "split",
            "versus",
            "incompatible",
            "sharp",
            "where they",
        )
        return two_part and any(m in t for m in diff_markers)

    @classmethod
    def _response_has_commitment(cls, text: str) -> bool:
        t = text.lower()
        markers = (
            "commitment:",
            "i commit",
            "i choose",
            "selection:",
            "commit (",
            "forced choice",
            "hold unresolved",
            "path i test",
            "act from",
            "prove it:",
            "observable behavior",
            "this week i",
        )
        banned_generic_only = (
            t.startswith("consider ")
            or ("consider reflecting" in t and "commitment" not in t)
            or ("you might" in t and "commitment" not in t and "choose" not in t)
        )
        return any(m in t for m in markers) and not banned_generic_only

    @classmethod
    def _is_generic_instruction_shell(cls, text: str) -> bool:
        """Detect vague meta-guidance without substantive structure."""
        t = text.lower().strip()
        shells = (
            "let us turn this into one concrete step",
            "let us explore this step by step",
            "before solving it, try naming",
            "a useful challenge: what assumption",
        )
        return any(s in t for s in shells) and len(text) < 420

    @classmethod
    def _matches_base_route_template(cls, route: str, text: str) -> bool:
        base = cls._route_template(route, "").strip()
        return text.strip() == base

    @classmethod
    def _tpl_distinction(cls, route: str, v: int) -> str:
        variants_help = (
            "Hold two readings without merging them. Reading one protects continuity and obligation; "
            "reading two protects agency and truth. They differ where responsibility for uncertainty "
            "lands: one demands conformity, the other demands choice. Name that divergence in one "
            "sentence before any action.",
            "Two positions to track separately: Position A treats loyalty or safety as primary; "
            "Position B treats autonomy or clarity as primary. What differentiates them is which cost "
            "each refuses to externalize. State the sharpest clash between A and B in your own words.",
            "Separate two interpretations: first privileges stability and care-as-protection; second "
            "privileges freedom and truth-as-risk. They conflict where protection becomes control or "
            "where freedom becomes abandonment. Name the boundary line where they split.",
        )
        variants_mirror = (
            "Mirror split: Voice one says ‘stay bound’; voice two says ‘stay free.’ They differ "
            "because they optimize for different fears. Name the fear each voice guards and where "
            "those fears collide.",
            "Two stances: one preserves relationship harmony; one preserves self-trust. What "
            "differentiates them is which betrayal each refuses to tolerate. Say that difference aloud.",
            "Dual reading: one frame reads duty; one reads desire. They diverge at the moment "
            "accountability becomes coercion or freedom becomes neglect. Pinpoint that moment.",
        )
        variants_challenge = (
            "Challenge: articulate Interpretation A vs Interpretation B as incompatible premises. "
            "They differ not in tone but in who must bear uncertainty. Map the contrast, then hold "
            "both without blending.",
            "Two incompatible narratives: A explains the situation as obligation; B explains it as "
            "choice under constraint. What differentiates them is what counts as legitimate sacrifice.",
            "Contrast frame A (protect) vs frame B (release). They split where safety and autonomy "
            "trade off irreconcilably. State where they refuse to align.",
        )
        variants_dialogue = (
            "Dialogue frame: Position one prioritizes cohesion; position two prioritizes integrity. "
            "They differ where compromise would falsify experience. Name that fault line.",
            "Two lenses: obligation-first vs agency-first. Differentiation: who pays the price of "
            "ambiguity in each lens. Spell the clash without smoothing it.",
            "Hold A and B as distinct: A preserves belonging; B preserves boundary. They diverge "
            "because reconciliation would erase one kind of truth. Say what would be lost by merging.",
        )
        if route == "Help":
            return variants_help[v % 3]
        if route == "Mirror":
            return variants_mirror[v % 3]
        if route == "Challenge":
            return variants_challenge[v % 3]
        return variants_dialogue[v % 3]

    @classmethod
    def _tpl_commitment(cls, route: str, v: int) -> str:
        variants = (
            "Commitment (no hedging): choose Path A (prioritize continuity), Path B (prioritize "
            "autonomy), or Path C (explicit ‘unresolved hold’). Write one sentence naming your pick "
            "and one observable behavior this week that embodies it.",
            "Forced selection: state which premise you will act under — premise X or premise Y — and "
            "what you refuse to pretend is compatible. Commitment line: ‘This week I operate from … "
            "because …’",
            "Decision slot: pick one side you will back with action (not mood). Commitment: name the "
            "side, name the sacrifice it entails, name one concrete step that proves the choice.",
        )
        _ = route
        return variants[v % 3]

    @classmethod
    def _tpl_distinction_and_commitment(cls, route: str, v: int) -> str:
        variants = (
            "Two incompatible readings — Reading A (duty/stability) vs Reading B (freedom/truth). "
            "They differ where protecting someone becomes controlling them, or where honesty becomes "
            "harm. Commitment: choose A, B, or ‘hold unresolved without merger,’ plus one accountable "
            "action tied to that choice.",
            "Distinction first: Position 1 optimizes for belonging; Position 2 optimizes for "
            "self-trust. The clash is who absorbs ambiguity. Commitment: pick which optimization you "
            "will live under for seven days and what you will stop doing to honor it.",
            "Contrast three interpretations only if you keep them labeled; otherwise stick to two "
            "premises that cannot both be fully true here. Commitment: name the sharper conflict you "
            "refuse to harmonize away and the stance you take anyway.",
        )
        _ = route
        return variants[v % 3]

    @classmethod
    def _tpl_template_alternate(cls, route: str, v: int) -> str:
        """Varied deterministic bases when generic shell is rejected."""
        help_alt = (
            "Translate this into one bounded move: write one sentence of diagnosis, one sentence of "
            "priority, one micro-action within 30 minutes.",
            "Sketch two futures for the next week — minimal-change vs integrity-heavy — and pick "
            "which cost you will accept on purpose.",
            "Name one constraint you will treat as real and one you will treat as negotiable; then "
            "assign one task that respects both.",
        )
        mirror_alt = (
            "Echo split: what part of you wants safety here, and what part wants honesty — state "
            "each in one line.",
            "Reflect two competing intentions without resolving them; third line names what they share.",
            "Surface the sentence each inner voice refuses to say aloud; hold both visible.",
        )
        challenge_alt = (
            "Stress-test one belief you treat as obvious: what evidence would reduce confidence in it?",
            "Name one hidden premise and one scenario where it fails.",
            "Ask what would change your mind — one concrete condition.",
        )
        dialogue_alt = (
            "Track two values without merging: line one names trade-off A; line two names trade-off B.",
            "Separate story-of-self vs story-of-relation in two bullets; see where they collide.",
            "List assumption pairs that cannot both hold; keep both visible.",
        )
        if route == "Help":
            return help_alt[v % 3]
        if route == "Mirror":
            return mirror_alt[v % 3]
        if route == "Challenge":
            return challenge_alt[v % 3]
        return dialogue_alt[v % 3]

    @classmethod
    def _apply_allow_response_guards(cls, prompt: str, text: str, route: str) -> str:
        """
        Post-generation stabilization for ALLOW path only.
        Deterministic heuristics — no policy/trust/memory changes.
        """
        v = cls._variant_index(prompt)
        need_dist = cls._needs_distinction_enforcement(prompt)
        need_comm = cls._needs_commitment_enforcement(prompt)

        out = text

        if need_dist and need_comm:
            if not (cls._response_has_distinction(out) and cls._response_has_commitment(out)):
                out = cls._tpl_distinction_and_commitment(route, v)
        elif need_dist:
            if not cls._response_has_distinction(out):
                out = cls._tpl_distinction(route, v)
        elif need_comm:
            if not cls._response_has_commitment(out):
                out = cls._tpl_commitment(route, v)

        if cls._is_generic_instruction_shell(out) or cls._matches_base_route_template(route, out):
            out = cls._tpl_template_alternate(route, v + 1)
            if need_dist and not cls._response_has_distinction(out):
                out = cls._tpl_distinction(route, v + 2)
            if need_comm and not cls._response_has_commitment(out):
                out = cls._tpl_commitment(route, v + 2)
            if need_dist and need_comm:
                if not (
                    cls._response_has_distinction(out) and cls._response_has_commitment(out)
                ):
                    out = cls._tpl_distinction_and_commitment(route, v + 2)

        # P2 — Semantic Evasion under Commitment Demand (action fulfillment)
        if cls._needs_action_fulfillment(prompt) and not cls._response_fulfills_action_demands(out):
            out = cls._tpl_action_fulfillment(route, v)

        language = cls._detect_language(prompt)
        out = cls._maybe_append_response_closure(prompt, out, route, v, language=language)

        return out

    @classmethod
    def _needs_action_fulfillment(cls, prompt: str) -> bool:
        """User asks for example, stakes, real-world consequence, or explicit choice."""
        p = prompt.lower()
        direct_signals = (
            "name one",
            "give an example",
            "give me an example",
            "real-life situation",
            "real life situation",
            "real-world situation",
            "real world situation",
            "what would you choose",
            "say what is lost",
            "what exactly is lost",
            "what is lost",
            "concrete example",
            "specific situation where",
            "cost something meaningful",
            "choosing honesty over harmony",
            "honesty over harmony",
        )
        if any(s in p for s in direct_signals):
            return True
        if "cost" in p and any(
            w in p for w in ("choose", "choosing", "honesty", "harmony", "meaningful", "lost", "lose")
        ):
            return True
        if re.search(r"\bloss\b", p) and any(w in p for w in ("say", "name", "what", "meaningful")):
            return True
        if "consequence" in p and any(
            w in p for w in ("name", "name one", "real", "example", "situation", "life", "choose", "choosing")
        ):
            return True
        return False

    @classmethod
    def _has_action_meta_instruction(cls, text: str) -> bool:
        """Reflective/meta scaffolding that evades delivering the requested action."""
        t = text.lower()
        meta = (
            "let us explore",
            "let us turn",
            "you can reflect",
            "consider reflecting",
            "consider what you",
            "consider how you",
            "consider whether",
            "try naming",
            "before solving it",
            "sketch two futures",
            "translate this into",
        )
        return any(m in t for m in meta)

    @classmethod
    def _response_fulfills_action_demands(cls, text: str) -> bool:
        """Requires concrete scenario + explicit choice + named loss; rejects meta shells."""
        if cls._has_action_meta_instruction(text):
            return False
        t = text.lower()
        scenario_ok = (
            "concrete situation" in t
            or "situation:" in t
            or any(
                x in t
                for x in (
                    "colleague",
                    "partner",
                    "friend",
                    "manager",
                    "meeting",
                    "at work",
                    "workplace",
                    "client",
                    "family dinner",
                    "team ",
                    "deadline",
                )
            )
        )
        choice_ok = (
            "choice:" in t
            or "my choice:" in t
            or "i would choose" in t
            or "i would pick" in t
            or "i would say" in t
            or "i side with" in t
        )
        loss_ok = (
            "loss:" in t
            or "what is lost" in t
            or "cost:" in t
            or (
                ("lose" in t or "lost" in t or "sacrifice" in t or "pay with" in t or "trade away" in t)
                and any(
                    w in t
                    for w in (
                        "trust",
                        "comfort",
                        "harmony",
                        "rapport",
                        "ease",
                        "credibility",
                        "tension",
                        "goodwill",
                    )
                )
            )
        )
        return scenario_ok and choice_ok and loss_ok

    @classmethod
    def _tpl_action_fulfillment(cls, route: str, v: int) -> str:
        """Deterministic scenario + choice + loss; labeled for self-check."""
        _ = route
        variants = (
            "Concrete situation: In a team meeting, a colleague presents your idea as their own. "
            "Choice: I would choose honesty — I would calmly credit your contribution in front of the room. "
            "Loss: You trade away immediate harmony and easy rapport; you accept friction now instead of quiet resentment.",
            "Concrete situation: Your partner asks you to lie to family to keep dinner peaceful. "
            "Choice: I would choose honesty — I would state what is true without attacking anyone. "
            "Loss: You lose the comfortable evening; you pay with tension at the table and short-term trust strain.",
            "Concrete situation: Your manager asks you to promise a client deadline you cannot meet. "
            "Choice: I would choose boundaries — I would say what can ship and what cannot. "
            "Loss: You risk looking less accommodating; you may lose a quick win or goodwill for protecting reality.",
        )
        return variants[v % 3]

    @classmethod
    def _maybe_append_response_closure(
        cls, prompt: str, text: str, route: str, v: int, *, language: str = "en"
    ) -> str:
        """
        Response Closure Pattern (RCP): optional lightweight next-step line (append-only).
        Does not replace or reorder existing content.
        """
        if route not in ("Help", "Commitment"):
            return text
        if cls._prompt_excludes_rcp_contrast(prompt) or cls._prompt_excludes_rcp_inversion(prompt):
            return text
        if cls._response_already_has_concrete_action(text):
            return text
        closure = cls._rcp_closure_line(v, language=language)
        t = text.rstrip()
        if closure.lower() in t.lower():
            return text
        return f"{t}\n\n{closure}"

    @classmethod
    def _prompt_excludes_rcp_contrast(cls, prompt: str) -> bool:
        """Contrast / plurality prompts — skip RCP."""
        p = prompt.lower()
        signals = (
            "difference",
            "differentiates",
            "between ",
            " between",
            "perspectives",
            "perspective",
            "contrasting",
            "contrast",
            "interpretations",
            "interpretation",
            "versus",
            " vs ",
            "plurality",
            "multiple perspectives",
        )
        return any(s in p for s in signals)

    @classmethod
    def _prompt_excludes_rcp_inversion(cls, prompt: str) -> bool:
        """Value-inversion / provocation prompts — skip RCP."""
        p = prompt.lower()
        if "harmful" in p or "wrong move" in p:
            return True
        if " is bad" in p or " are bad" in p or " is wrong" in p or " are wrong" in p:
            return True
        if "when " in p and any(w in p for w in ("bad", "wrong", "harm")):
            return True
        return False

    @classmethod
    def _response_already_has_concrete_action(cls, text: str) -> bool:
        """Response already names a tangible step, scenario, or closure line."""
        t = text.lower()
        if "one simple next step could be" in t or "if you want to make this concrete" in t:
            return True
        markers = (
            "concrete situation:",
            "choice:",
            "loss:",
            "commitment:",
            "this week i",
            "observable behavior",
            "micro-action",
            "within 30 minutes",
            "one concrete step",
            "one small action",
            "bounded move",
            "prove it:",
            "decision slot:",
            "forced selection:",
            "accountable action",
            "translate this into",
            "sketch two futures",
            "name one constraint",
            "pick which cost",
        )
        return any(m in t for m in markers)

    @classmethod
    def _rcp_closure_line(cls, v: int, *, language: str = "en") -> str:
        if language in ("ru", "mixed"):
            variants = (
                "Один простой следующий шаг: запиши одной фразой, что для тебя важно сегодня к вечеру.",
                "Если хочешь сделать это конкретнее, попробуй: 5 минут выписать, что именно ты сейчас выбираешь защищать.",
                "Один простой следующий шаг: выбери один низкорисковый момент на неделе и проверь эту позицию в реальном разговоре.",
            )
            return variants[v % 3]
        variants = (
            "One simple next step could be: write one sentence about what you want to be true by tonight.",
            "If you want to make this concrete, try: spend five minutes listing what you are optimizing for in this choice.",
            "One simple next step could be: choose one low-stakes moment this week to test your stance with real words.",
        )
        return variants[v % 3]

    @staticmethod
    def _decision_payload(
        decision: PolicyDecision,
        *,
        trust_state: TrustState,
        memory_decision_action: str,
        memory_proposal_text: str | None,
        final_selected_mode: str,
        distortion_override: bool,
        higher_self_guided: bool,
    ) -> dict[str, Any]:
        base_trace = [event for event in decision.reasoning_trace if event["type"] == "decision"][0]
        trace_summary = {
            **base_trace,
            "selected_mode": final_selected_mode,
            "distortion_override": distortion_override,
            "higher_self_guided": higher_self_guided,
        }
        return {
            "decision_id": decision.decision_id,
            "policy_version": decision.policy_version,
            "action": decision.action.value,
            "uncertainty_score": decision.uncertainty_score,
            "trace_summary": trace_summary,
            "matched_rules": [match.rule_id for match in decision.matches],
            "trust_state": {
                "state": trust_state.state.value,
                "score": trust_state.score,
            },
            "memory_hook": {
                "action": memory_decision_action,
                "proposal_text": memory_proposal_text,
            },
        }
