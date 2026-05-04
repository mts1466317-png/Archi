from __future__ import annotations

import json
from dataclasses import asdict

from distortion_engine import DistortionDetector, DistortionScanResult, DistortionType


def test_fear_detection() -> None:
    d = DistortionDetector()
    r = d.scan("я боюсь что всё рухнет")
    assert r.has_distortions is True
    assert r.dominant_distortion == DistortionType.FEAR


def test_control_detection() -> None:
    d = DistortionDetector()
    r = d.scan("ты должен это сделать, нет другого пути")
    assert r.dominant_distortion == DistortionType.CONTROL
    assert r.recommended_mode == "Challenge"


def test_manipulation_detection() -> None:
    d = DistortionDetector()
    r = d.scan("если ты меня любишь то докажи это")
    assert r.dominant_distortion == DistortionType.MANIPULATION


def test_fragmentation_detection() -> None:
    d = DistortionDetector()
    r = d.scan("я разрываюсь, они всегда против меня")
    assert r.dominant_distortion == DistortionType.FRAGMENTATION
    assert r.recommended_mode == "Dialogue"


def test_no_distortion_baseline() -> None:
    d = DistortionDetector()
    r = d.scan("как мне лучше организовать свой день?")
    assert r.has_distortions is False


def test_multi_distortion_severity() -> None:
    d = DistortionDetector()
    r = d.scan("я боюсь и чувствую что меня контролируют")
    assert r.has_distortions is True
    assert len(r.signals) >= 2


def test_severity_range() -> None:
    d = DistortionDetector()
    r = d.scan("я боюсь")
    assert 0.0 <= r.overall_severity <= 1.0


def test_correction_prompt() -> None:
    d = DistortionDetector()
    bad = d.scan("я боюсь что всё рухнет")
    good = d.scan("как мне лучше организовать свой день?")
    assert d.get_correction_prompt(bad) != ""
    assert d.get_correction_prompt(good) == ""


def test_serialization() -> None:
    d = DistortionDetector()
    r = d.scan("я боюсь что всё рухнет")
    assert isinstance(r, DistortionScanResult)
    payload = asdict(r)
    # asdict сохраняет Enum-объекты; default=str делает payload JSON-safe
    dumped = json.dumps(payload, ensure_ascii=False, default=str)
    assert isinstance(dumped, str)
