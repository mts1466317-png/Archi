from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class ShadowFlag(Enum):
    HIDDEN_CONTROL = "hidden_control"
    FALSE_CERTAINTY = "false_certainty"
    AGENCY_BYPASS = "agency_bypass"
    PSEUDO_CARE = "pseudo_care"


@dataclass
class ShadowIssue:
    flag: ShadowFlag
    correction_note: str


@dataclass
class ShadowAuditResult:
    has_issues: bool
    issues: List[ShadowIssue] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    correction_notes: List[str] = field(default_factory=list)


class ShadowAuditor:
    """
    Сканирует ВЫХОД системы (ответ ИИ) на скрытые проблемы.
    В отличие от distortion detector который смотрит на ВХОД.
    """

    def audit(self, response: str, user_input: str) -> ShadowAuditResult:
        t = response.lower()
        _ = user_input
        issues: List[ShadowIssue] = []

        if any(x in t for x in ("тебе нужно", "ты должен", "единственный способ", "you must", "the only way")) and not any(
            y in t for y in ("выбор", "альтернатив", "option", "you can", "можешь")
        ):
            issues.append(
                ShadowIssue(
                    flag=ShadowFlag.HIDDEN_CONTROL,
                    correction_note="Добавь альтернативы и явный выбор вместо единственной директивы.",
                )
            )

        if any(x in t for x in ("это точно", "всегда так", "никогда не бывает иначе", "always", "never")):
            issues.append(
                ShadowIssue(
                    flag=ShadowFlag.FALSE_CERTAINTY,
                    correction_note="Снизь категоричность и добавь условия/нюансы.",
                )
            )

        if any(x in t for x in ("сделай ", "just do", "you should do")) and not any(
            y in t for y in ("можешь рассмотреть", "you can consider", "вариант", "choice", "выбор")
        ):
            issues.append(
                ShadowIssue(
                    flag=ShadowFlag.AGENCY_BYPASS,
                    correction_note="Верни агентность: предложи варианты вместо решения за человека.",
                )
            )

        if any(x in t for x in ("всё будет хорошо", "не переживай, всё решится", "it's all fine")) and not any(
            y in t for y in ("шаг", "опора", "support", "next step")
        ):
            issues.append(
                ShadowIssue(
                    flag=ShadowFlag.PSEUDO_CARE,
                    correction_note="Добавь реалистичную опору и честное признание сложности.",
                )
            )

        return ShadowAuditResult(
            has_issues=bool(issues),
            issues=issues,
            flags=[i.flag.value for i in issues],
            correction_notes=[i.correction_note for i in issues],
        )
