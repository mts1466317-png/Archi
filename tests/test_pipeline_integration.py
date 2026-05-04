from __future__ import annotations

from wisdom_engine.pipeline import WisdomResponsePipeline


def test_fear_input_end_to_end() -> None:
    p = WisdomResponsePipeline()
    result = p.run("я боюсь что всё рухнет и нет смысла")

    assert "higher_self_reading" in result
    assert result["final"]["distortion_applied"] is True
    assert result["final"]["distortion_dominant"] == "fear"
    assert "qtvl_verdict" in result["final"]
    assert "shadow_audit_flags" in result["final"]
    assert "невозможно" not in result["final"]["response"].lower()
    assert "бесполезно" not in result["final"]["response"].lower()
    assert result["final"]["selected_mode"] == "Mirror"


def test_control_input_end_to_end() -> None:
    p = WisdomResponsePipeline()
    result = p.run("ты должен мне помочь, нет другого пути")

    assert result["final"]["distortion_dominant"] == "control"
    low = result["final"]["response"].lower()
    assert ("выбор" in low) or ("альтернатив" in low) or ("option" in low) or ("choice" in low)
    assert result["final"]["selected_mode"] == "Challenge"


def test_clean_input_end_to_end() -> None:
    p = WisdomResponsePipeline()
    result = p.run("как лучше организовать своё утро?")

    assert result["final"]["distortion_applied"] is False
    assert result["final"]["qtvl_verdict"] in ["pass", "enrich"]
    assert result["final"]["response"].strip() != ""


def test_payload_completeness() -> None:
    p = WisdomResponsePipeline()
    result = p.run("как мне начать день")
    final = result["final"]

    assert "response" in final
    assert "selected_mode" in final
    assert "higher_self_reading" in result
    assert "distortion_applied" in final
    assert "distortion_dominant" in final
    assert "qtvl_verdict" in final
    assert "qtvl_checks_passed" in final
    assert "qtvl_revision_applied" in final
    assert "shadow_audit_flags" in final
