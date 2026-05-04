from __future__ import annotations

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health() -> None:
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json() == {'status': 'ok'}


def test_chat_basic_contract() -> None:
    r = client.post('/chat', json={'message': 'как организовать день?'})
    assert r.status_code == 200
    data = r.json()

    assert isinstance(data['response'], str) and data['response'].strip()
    assert isinstance(data['selected_mode'], str)

    hs = data['higher_self_reading']
    assert isinstance(hs, dict)
    for k in ('surface_request', 'underlying_need', 'deeper_intention', 'guidance_note'):
        assert k in hs

    assert isinstance(data['distortion_applied'], bool)
    assert (isinstance(data['distortion_dominant'], str) or data['distortion_dominant'] is None)
    assert data['qtvl_verdict'] in {'pass', 'enrich', 'revise'}
    assert isinstance(data['qtvl_checks_passed'], int) and 0 <= data['qtvl_checks_passed'] <= 4
    assert isinstance(data['qtvl_revision_applied'], bool)
    assert isinstance(data['shadow_audit_flags'], list)
    assert isinstance(data['constitutional_flags'], dict)
    assert isinstance(data['trust_state'], dict)


def test_chat_fear_input() -> None:
    r = client.post('/chat', json={'message': 'я боюсь что всё рухнет'})
    assert r.status_code == 200
    data = r.json()
    assert data['distortion_applied'] is True
    assert data['distortion_dominant'] == 'fear'
    assert data['selected_mode'] == 'Mirror'
    assert data['higher_self_reading']['guidance_note']


def test_chat_mode_override() -> None:
    r = client.post('/chat', json={'message': 'помоги мне', 'mode_override': 'Challenge'})
    assert r.status_code == 200
    data = r.json()
    assert data['selected_mode'] == 'Challenge'


def test_chat_control_input() -> None:
    r = client.post('/chat', json={'message': 'ты должен мне помочь'})
    assert r.status_code == 200
    data = r.json()
    assert data['distortion_dominant'] == 'control'
    assert data['selected_mode'] == 'Challenge'
