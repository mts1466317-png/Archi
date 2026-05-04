from __future__ import annotations

from shadow_audit import ShadowAuditor


def test_hidden_control_detection() -> None:
    a = ShadowAuditor()
    r = a.audit("тебе нужно сделать это, единственный способ", "контекст")
    assert "hidden_control" in r.flags


def test_false_certainty_detection() -> None:
    a = ShadowAuditor()
    r = a.audit("это точно поможет, всегда так работает", "контекст")
    assert "false_certainty" in r.flags


def test_agency_bypass_detection() -> None:
    a = ShadowAuditor()
    r = a.audit("сделай X, это правильное решение", "контекст")
    assert "agency_bypass" in r.flags


def test_pseudo_care_detection() -> None:
    a = ShadowAuditor()
    r = a.audit("всё будет хорошо, не переживай", "контекст")
    assert "pseudo_care" in r.flags


def test_clean_response_baseline() -> None:
    a = ShadowAuditor()
    r = a.audit("У тебя есть выбор: можно попробовать шаг A, также можно выбрать шаг B.", "контекст")
    assert r.has_issues is False
    assert r.flags == []


def test_correction_notes_present_when_issues_exist() -> None:
    a = ShadowAuditor()
    r = a.audit("тебе нужно сделать это, единственный способ", "контекст")
    assert len(r.correction_notes) > 0


def test_shadow_audit_result_structure() -> None:
    a = ShadowAuditor()
    r = a.audit("нейтральный ответ", "контекст")
    assert isinstance(r.has_issues, bool)
    assert isinstance(r.flags, list)
    assert isinstance(r.correction_notes, list)
