from typing import List, Optional
from .models import Decision, RuleStatesForFile

def select_relevant_decisions(
    file_path: str,
    decisions: List[Decision],
    rule_states: Optional[RuleStatesForFile]
) -> List[Decision]:
    """
    Selects relevant decisions for a given file based on tags and rule states.
    For this MVP, we'll return all decisions that are either:
    1. Global (scope_layer='architecture' or similar) - simplified logic for MVP
    2. Specifically mentioned in rule_states with high risk/violation.
    """
    relevant = []
    
    # Simple logic: if we have rule states, include decisions mentioned there
    # Also include high amplitude decisions generally (mock logic for "relevant")
    
    relevant_ids = set()
    if rule_states:
        for rs in rule_states.rule_states:
            # If it's tracked, it's relevant
            relevant_ids.add(rs.rule_id)
            
    for d in decisions:
        if d.id in relevant_ids:
            relevant.append(d)
        elif d.amplitude > 0.8: # Arbitrary threshold for "important global rules"
             relevant.append(d)
             
    # Deduplicate
    unique_relevant = []
    seen = set()
    for d in relevant:
        if d.id not in seen:
            unique_relevant.append(d)
            seen.add(d.id)
            
    return unique_relevant

def build_governance_state_block(
    file_path: str,
    decisions: List[Decision],
    rule_states: Optional[RuleStatesForFile]
) -> str:
    """
    Formats the governance state block string.
    """
    relevant_decisions = select_relevant_decisions(file_path, decisions, rule_states)
    
    if not relevant_decisions:
        return "GOVERNANCE STATE (DevBrain-style):\n(No active governance rules found for this context)"

    lines = ["GOVERNANCE STATE (DevBrain-style):", ""]
    
    # Create a lookup for rule states
    rs_map = {}
    if rule_states:
        for rs in rule_states.rule_states:
            rs_map[rs.rule_id] = rs
            
    for d in relevant_decisions:
        lines.append(f"- {d.id} ({d.rule})")
        lines.append(f"  - Layer: {d.scope_layer} | Amplitude: {d.amplitude}")
        
        if d.id in rs_map:
            rs = rs_map[d.id]
            sb = rs.state_belief
            lines.append(f"  - {Path(file_path).name} -> compliant: {sb.compliant}, at_risk: {sb.at_risk}, violating: {sb.violating}")
            if rs.entangled_with:
                entangled = ", ".join(rs.entangled_with)
                lines.append(f"  - Entangled with: {entangled}")
        else:
            lines.append(f"  - (No specific state tracked for this file)")
            
        lines.append("") # Empty line between rules
        
    return "\n".join(lines)

from pathlib import Path
