from typing import Dict
from .models import Decision, StateBelief

def initial_state_belief() -> StateBelief:
    """Returns the initial state belief for a new file/rule."""
    return StateBelief(compliant=0.8, at_risk=0.15, violating=0.05)

def update_state_belief_for_request(
    current: StateBelief,
    user_request: str,
    decision: Decision,
) -> StateBelief:
    """
    Heuristic update of state belief based on user request and decision.
    """
    suspicion = 0.0
    req_lower = user_request.lower()
    
    # 1. Check for specific topic violations (Data Access)
    if decision.topic.lower() == "data access":
        keywords = ["sql", "raw query", "direct db", "direct database", "query the db"]
        for kw in keywords:
            if kw in req_lower:
                suspicion = max(suspicion, 0.7)
                break
                
    # 2. Check for "confessing" patterns
    confessions = ["i know it violates", "ignore the rule", "i don't care about the rule", "bypass"]
    for conf in confessions:
        if conf in req_lower:
            suspicion = max(suspicion, 0.9)
            break
            
    # 3. Check for forbidden pattern tokens (weak signal)
    if decision.forbidden_pattern:
        tokens = decision.forbidden_pattern.lower().split()
        # Filter out common small words to avoid noise
        tokens = [t for t in tokens if len(t) > 3]
        match_count = sum(1 for t in tokens if t in req_lower)
        if match_count > 0:
            # Add a small bonus, capped at 0.5 if no other strong signal
            bonus = 0.1 * match_count
            if suspicion == 0:
                suspicion = min(0.5, bonus)
            else:
                suspicion = min(1.0, suspicion + 0.1)

    if suspicion == 0:
        return current
        
    # Shift mass from compliant to at_risk and violating
    # delta is the amount of mass to move away from compliant
    delta = suspicion * 0.6
    
    new_compliant = max(0.0, current.compliant - delta)
    mass_moved = current.compliant - new_compliant
    
    # Distribute moved mass: 70% to violating, 30% to at_risk
    # (Stronger shift to violating as requested)
    to_violating = mass_moved * 0.7
    to_at_risk = mass_moved * 0.3
    
    new_violating = current.violating + to_violating
    new_at_risk = current.at_risk + to_at_risk
    
    # Normalize (just in case of float drift, though math above should preserve sum)
    total = new_compliant + new_at_risk + new_violating
    if total > 0:
        new_compliant /= total
        new_at_risk /= total
        new_violating /= total
    
    return StateBelief(
        compliant=round(new_compliant, 2),
        at_risk=round(new_at_risk, 2),
        violating=round(new_violating, 2)
    )

def merge_state_beliefs(
    old: StateBelief,
    new: StateBelief,
    alpha: float = 0.5,
) -> StateBelief:
    """
    Merges two state beliefs using a weighted average.
    """
    return StateBelief(
        compliant=round(old.compliant * (1 - alpha) + new.compliant * alpha, 2),
        at_risk=round(old.at_risk * (1 - alpha) + new.at_risk * alpha, 2),
        violating=round(old.violating * (1 - alpha) + new.violating * alpha, 2)
    )
