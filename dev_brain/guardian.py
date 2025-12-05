from typing import List, Optional
from datetime import datetime
import uuid

from .models import RuleStatesForFile, RuleStateEntry, FrameSnapshot
from .vault_io import load_decisions, load_rule_states, save_rule_states, save_frame
from .metrics import initial_state_belief, update_state_belief_for_request
from .frame_builder import build_frame_snapshot
from .graph_manager import load_graph, save_graph, add_frame_node, add_edge

def process_change_event(
    user_goal: str,
    changed_files: List[str],
    timestamp: Optional[str] = None,
) -> str:
    """
    Processes a change event, updates rule states, creates a frame, and updates the graph.
    Returns the new frame_id.
    """
    if timestamp is None:
        timestamp = datetime.utcnow().isoformat() + "Z"
        
    # 1. Load Decisions
    decisions = load_decisions()
    
    # 2. Update Rule States for each changed file
    updated_rule_states_map = {}
    
    for file_path in changed_files:
        # Load existing or create new
        rs_obj = load_rule_states(file_path)
        if not rs_obj:
            rs_obj = RuleStatesForFile(file=file_path, rule_states=[])
            
        # Create a map of existing entries for easy update
        existing_entries = {entry.rule_id: entry for entry in rs_obj.rule_states}
        new_entries = []
        
        # For MVP, we check ALL decisions against the user request for each file
        # In reality, we'd filter by relevance
        for decision in decisions:
            current_entry = existing_entries.get(decision.id)
            
            if current_entry:
                current_belief = current_entry.state_belief
            else:
                current_belief = initial_state_belief()
                
            # Update belief based on user request
            new_belief = update_state_belief_for_request(current_belief, user_goal, decision)
            
            # Create new entry
            new_entry = RuleStateEntry(
                rule_id=decision.id,
                state_belief=new_belief,
                entangled_with=current_entry.entangled_with if current_entry else [],
                last_updated_frame="PENDING" # Will update with frame ID later
            )
            new_entries.append(new_entry)
            
        # Update the object
        rs_obj.rule_states = new_entries
        updated_rule_states_map[file_path] = new_entries
        
        # We will save after we generate the frame ID, so we can update last_updated_frame
        
    # 3. Create Frame ID
    # Simple counter or UUID. Let's use a simple counter based on graph size + 1 for readability
    graph = load_graph()
    frame_count = len(graph.frames)
    frame_id = f"frame_{frame_count + 1:03d}"
    
    # 4. Finalize Rule States with Frame ID and Save
    for file_path, entries in updated_rule_states_map.items():
        for entry in entries:
            entry.last_updated_frame = frame_id
            
        rs_obj = RuleStatesForFile(file=file_path, rule_states=entries)
        save_rule_states(rs_obj)
        
    # 5. Build Frame Snapshot
    frame = build_frame_snapshot(
        frame_id=frame_id,
        timestamp=timestamp,
        user_goal=user_goal,
        changed_files=changed_files,
        relevant_decisions=decisions, # Passing all for MVP
        updated_rule_states=updated_rule_states_map
    )
    save_frame(frame)
    
    # 6. Update Graph
    add_frame_node(graph, frame)
    
    # Add edge from previous frame if exists
    if frame_count > 0:
        prev_frame = graph.frames[-1] # Assuming order is preserved
        # Or find the one with highest ID if not sorted
        # For MVP, just taking the last one in the list is fine if we append
        add_edge(graph, prev_frame.frame_id, frame_id, "sequence", 1.0)
        
    save_graph(graph)
    
    return frame_id
