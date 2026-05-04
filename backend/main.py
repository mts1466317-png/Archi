from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from wisdom_engine.pipeline import WisdomResponsePipeline


app = FastAPI(
    title="Archi AI",
    description="Guide Intelligence System",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
pipeline = WisdomResponsePipeline()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = None
    suppress_recall: bool = False
    mode_override: str | None = None


class ChatResponse(BaseModel):
    response: str
    selected_mode: str
    risks_detected: list[str]
    constitutional_flags: dict[str, bool]
    decision_id: str
    policy_version: str
    action_taken: str
    uncertainty_score: float
    matched_rules: list[str]
    trace_summary: dict[str, Any]
    session_id: str
    trust_state: dict[str, Any]
    memory_hook: dict[str, Any]

    higher_self_reading: dict[str, Any] | None
    distortion_applied: bool
    distortion_dominant: str | None
    qtvl_verdict: str
    qtvl_checks_passed: int
    qtvl_revision_applied: bool
    shadow_audit_flags: list[str]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    session_id = payload.session_id or str(uuid4())
    result = pipeline.run(
        payload.message,
        session_id=session_id,
        suppress_recall=payload.suppress_recall,
        mode_override=payload.mode_override,
    )

    selected_mode = result["final"]["selected_mode"]
    response = result["final"]["response"]
    distortion_scan = result["pipeline"]["step_2_distortion_scan"]
    constitutional = result["pipeline"]["step_3_constitutional_check"]

    constitutional_checks = constitutional.get("checks", {})
    constitutional_flags = {
        check_name: check_data.get("passed", False)
        for check_name, check_data in constitutional_checks.items()
    }

    return ChatResponse(
        response=response,
        selected_mode=selected_mode,
        risks_detected=distortion_scan.get("detected_risks", []),
        constitutional_flags=constitutional_flags,
        decision_id=result["decision"]["decision_id"],
        policy_version=result["decision"]["policy_version"],
        action_taken=result["decision"]["action"],
        uncertainty_score=result["decision"]["uncertainty_score"],
        matched_rules=result["decision"]["matched_rules"],
        trace_summary=result["decision"]["trace_summary"],
        session_id=session_id,
        trust_state=result["decision"]["trust_state"],
        memory_hook=result["decision"]["memory_hook"],
        higher_self_reading=result.get("higher_self_reading"),
        distortion_applied=result["final"].get("distortion_applied", False),
        distortion_dominant=result["final"].get("distortion_dominant"),
        qtvl_verdict=result["final"].get("qtvl_verdict", "pass"),
        qtvl_checks_passed=result["final"].get("qtvl_checks_passed", 0),
        qtvl_revision_applied=result["final"].get("qtvl_revision_applied", False),
        shadow_audit_flags=result["final"].get("shadow_audit_flags", []),
    )
