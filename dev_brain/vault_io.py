import json
from typing import List, Optional
from pathlib import Path
from .models import Decision, FileSummary, RuleStatesForFile, FrameSnapshot
from .paths import decisions_path, summary_path_for, rule_state_path_for, get_vault_root

def load_decisions() -> List[Decision]:
    """Loads all decisions from decisions.json."""
    path = decisions_path()
    if not path.exists():
        return []
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Decision(**item) for item in data]
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading decisions from {path}: {e}")
        return []

def load_file_summary(file_path: str) -> Optional[FileSummary]:
    """Loads the summary for a specific file."""
    path = summary_path_for(file_path)
    return load_file_summary_from_path(path)

def load_file_summary_from_path(path: Path) -> Optional[FileSummary]:
    """Loads the summary from a specific JSON path."""
    if not path.exists():
        return None
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return FileSummary(**data)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading summary from {path}: {e}")
        return None

def load_rule_states(file_path: str) -> Optional[RuleStatesForFile]:
    """Loads the rule states for a specific file."""
    path = rule_state_path_for(file_path)
    return load_rule_states_from_path(path)

def load_rule_states_from_path(path: Path) -> Optional[RuleStatesForFile]:
    """Loads the rule states from a specific JSON path."""
    if not path.exists():
        return None
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return RuleStatesForFile(**data)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading rule states from {path}: {e}")
        return None

def save_rule_states(rule_states: RuleStatesForFile) -> None:
    """Saves the rule states for a specific file."""
    path = rule_state_path_for(rule_states.file)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(rule_states.model_dump_json(indent=2))
    except IOError as e:
        print(f"Error saving rule states to {path}: {e}")

def save_frame(frame: FrameSnapshot) -> None:
    """Saves a frame snapshot."""
    path = get_vault_root() / "frames" / f"{frame.frame_id}.json"
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(frame.model_dump_json(indent=2))
    except IOError as e:
        print(f"Error saving frame to {path}: {e}")

