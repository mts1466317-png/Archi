from __future__ import annotations

from higher_self_engine import HigherSelfInterpreter


def test_surface_request_extraction() -> None:
    i = HigherSelfInterpreter()
    r = i.interpret("как заставить себя работать")
    assert r.surface_request != ""


def test_underlying_need_pressure_conflict() -> None:
    i = HigherSelfInterpreter()
    r = i.interpret("мне надо заставить себя, я должен начать")
    assert "конфликт" in r.underlying_need


def test_underlying_need_loss_of_support() -> None:
    i = HigherSelfInterpreter()
    r = i.interpret("я не могу и у меня не получается")
    assert "опоры" in r.underlying_need


def test_deeper_intention_not_empty() -> None:
    i = HigherSelfInterpreter()
    r = i.interpret("что мне делать")
    assert r.deeper_intention != ""


def test_guidance_note_not_empty() -> None:
    i = HigherSelfInterpreter()
    r = i.interpret("помоги решить")
    assert r.guidance_note != ""
    assert len(r.guidance_note) > 10


def test_higher_self_reading_structure() -> None:
    i = HigherSelfInterpreter()
    r = i.interpret("как мне жить")
    assert isinstance(r.surface_request, str) and r.surface_request is not None
    assert isinstance(r.underlying_need, str) and r.underlying_need is not None
    assert isinstance(r.deeper_intention, str) and r.deeper_intention is not None
    assert isinstance(r.guidance_note, str) and r.guidance_note is not None


def test_session_history_influence_no_crash() -> None:
    i = HigherSelfInterpreter()
    r = i.interpret("что мне делать", session_history=["раньше обсуждали тревогу"])
    assert r is not None
    assert r.guidance_note != ""
