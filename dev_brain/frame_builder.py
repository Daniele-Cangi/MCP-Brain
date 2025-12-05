from typing import List, Dict
from .models import FrameSnapshot, Decision, RuleStateEntry, SuspectedViolation, PredictedRisk, StateBelief

def build_frame_snapshot(
    frame_id: str,
    timestamp: str,
    user_goal: str,
    changed_files: List[str],
    relevant_decisions: List[Decision],
    updated_rule_states: Dict[str, List[RuleStateEntry]],
) -> FrameSnapshot:
    """
    Builds a FrameSnapshot object from the given data.
    """
    
    # 1. Identify suspected violations
    suspected_violations = []
    
    # Check updated rule states for high risk/violations
    for file_path, entries in updated_rule_states.items():
        for entry in entries:
            sb = entry.state_belief
            # Heuristic: if at_risk > 0.4 or violating > 0.2, flag it
            if sb.at_risk > 0.4 or sb.violating > 0.2:
                # Find the decision object to get the rule name/reason
                decision = next((d for d in relevant_decisions if d.id == entry.rule_id), None)
                reason = f"High risk detected for rule {entry.rule_id}"
                if decision:
                    reason = f"Potential violation of '{decision.rule}' in {file_path}"
                
                suspected_violations.append(SuspectedViolation(
                    decision_id=entry.rule_id,
                    reason=reason,
                    state_belief=sb,
                    status="suspected"
                ))

    # 2. Predicted risks (Placeholder for MVP)
    predicted_risks = []
    if len(suspected_violations) > 2:
        predicted_risks.append(PredictedRisk(
            type="COMPLIANCE_DRIFT",
            confidence=0.6,
            evidence=["multiple_violations_detected"]
        ))

    # 3. Next steps (Placeholder)
    next_steps = ["Review suspected violations", "Run full compliance check"]

    return FrameSnapshot(
        frame_id=frame_id,
        timestamp=timestamp,
        user_goal=user_goal,
        changed_files=changed_files,
        relevant_decisions=[d.id for d in relevant_decisions],
        suspected_violations=suspected_violations,
        predicted_risks=predicted_risks,
        next_steps=next_steps
    )
