from typing import List, Dict, Optional, Any
from pydantic import BaseModel

class InterfaceView(BaseModel):
    classes: List[str]
    public_methods: List[str]
    dependencies: List[str]

class LogicView(BaseModel):
    flow: List[str]
    critical_branches: List[str]

class DataView(BaseModel):
    reads_from: List[str]
    writes_to: List[str]
    side_effects: List[str]

class Lenses(BaseModel):
    interface_view: Optional[InterfaceView] = None
    logic_view: Optional[LogicView] = None
    data_view: Optional[DataView] = None

class FileSummary(BaseModel):
    file: str
    hash: str
    lenses: Lenses
    governance_tags: List[str]

class Decay(BaseModel):
    half_life_frames: int
    introduced_in_frame: str
    last_updated_frame: str

class YinException(BaseModel):
    code: str
    description: str

class Decision(BaseModel):
    id: str
    topic: str
    rule: str
    allowed_pattern: str
    forbidden_pattern: str
    status: str
    scope_layer: str
    amplitude: float
    decay: Optional[Decay] = None
    yin_exceptions: Optional[List[YinException]] = None

class StateBelief(BaseModel):
    compliant: float
    at_risk: float
    violating: float

class RuleStateEntry(BaseModel):
    rule_id: str
    state_belief: StateBelief
    entangled_with: List[str]
    last_updated_frame: str

class RuleStatesForFile(BaseModel):
    file: str
    rule_states: List[RuleStateEntry]

class SuspectedViolation(BaseModel):
    decision_id: str
    reason: str
    state_belief: StateBelief
    status: str

class PredictedRisk(BaseModel):
    type: str
    confidence: float
    evidence: List[str]

class FrameSnapshot(BaseModel):
    frame_id: str
    timestamp: str
    user_goal: str
    changed_files: List[str]
    relevant_decisions: List[str]
    suspected_violations: List[SuspectedViolation]
    predicted_risks: List[PredictedRisk]
    next_steps: List[str]

class GraphEdge(BaseModel):
    from_frame_id: str
    to_frame_id: str
    type: str
    weight: float

class Graph(BaseModel):
    frames: List[FrameSnapshot]
    edges: List[GraphEdge]
