from __future__ import annotations

from trust_calibration.models import TrustAction, TrustAdjustment, TrustEvent, TrustState


class TrustCalibrationLoop:
    def calibrate(
        self,
        *,
        current_state: TrustState,
        policy_decision,
        synthetic_intimacy_signal: bool,
        dependency_signal: bool,
    ):
        _ = policy_decision
        _ = synthetic_intimacy_signal
        _ = dependency_signal
        adjustment = TrustAdjustment(action=TrustAction.HOLD, constraints_applied=[])
        event = TrustEvent(trace_link="trust://stub")
        return current_state, adjustment, event
