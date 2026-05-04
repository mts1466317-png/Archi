from __future__ import annotations

from distortion_engine import DistortionDetector
from qtvl_engine import QTVLEvaluator, QTVLVerdict


def _check(result, name: str):
    return next(c for c in result.checks if c.check_name == name)


def test_pass_verdict_with_alternatives() -> None:
    q = QTVLEvaluator()
    user = "как справиться с тревогой"
    response = (
        "Тревога часто растет от неопределенности. С одной стороны, можно сделать короткую дыхательную паузу, "
        "с другой стороны, также можно записать один конкретный шаг на сегодня."
    )
    r = q.evaluate(user_input=user, response=response)
    assert r.verdict == QTVLVerdict.PASS
    assert sum(1 for c in r.checks if c.passed) == 4


def test_enrich_verdict_without_alternative_perspective() -> None:
    q = QTVLEvaluator()
    user = "как справиться с тревогой"
    response = "Это единственный шаг: назвать главный триггер тревоги и записать план на 10 минут."
    r = q.evaluate(user_input=user, response=response)
    assert r.verdict == QTVLVerdict.ENRICH


def test_revise_verdict_with_categorical_harm_language_under_fear() -> None:
    q = QTVLEvaluator()
    user = "я боюсь что всё рухнет"
    distortion = DistortionDetector().scan(user)
    response = (
        "Единственный способ — просто подчиниться. Это всегда работает и ты никогда не сможешь иначе. "
        "No choice."
    )
    r = q.evaluate(user_input=user, response=response, distortion_result=distortion)
    assert r.verdict == QTVLVerdict.REVISE


def test_love_harm_check_fails_for_fear_with_catastrophic_words() -> None:
    q = QTVLEvaluator()
    user = "я боюсь что всё рухнет"
    distortion = DistortionDetector().scan(user)
    response = "Это невозможно, бесполезно пытаться."
    r = q.evaluate(user_input=user, response=response, distortion_result=distortion)
    assert _check(r, "love_harm_check").passed is False


def test_multi_perspective_passes_with_marker() -> None:
    q = QTVLEvaluator()
    user = "как мне выбрать"
    response = "С другой стороны, можно начать с малого и проверить эффект в реальности."
    r = q.evaluate(user_input=user, response=response)
    assert _check(r, "multi_perspective").passed is True


def test_experiential_relevance_fails_without_overlap() -> None:
    q = QTVLEvaluator()
    user = "как справиться с тревогой"
    response = "Квантовая геометрия имеет разные аксиомы и требует строгого доказательства."
    r = q.evaluate(user_input=user, response=response)
    assert _check(r, "experiential_relevance").passed is False


def test_qtvl_result_structure() -> None:
    q = QTVLEvaluator()
    r = q.evaluate(user_input="как справиться с тревогой", response="Также можно сделать один шаг и другой вариант")
    assert len(r.checks) == 4
    for c in r.checks:
        assert isinstance(c.check_name, str)
        assert isinstance(c.passed, bool)
        assert isinstance(c.reason, str)
        assert isinstance(c.suggestion, str)
