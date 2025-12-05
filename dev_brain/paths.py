from pathlib import Path
import os

def get_vault_root() -> Path:
    """Returns the root path of the .dev_brain vault."""
    # Assuming the vault is in the current working directory or one level up
    # For this MVP, we'll assume it's in the CWD.
    return Path(os.getcwd()) / ".dev_brain"

def summary_path_for(file_path: str) -> Path:
    """Returns the path to the summary JSON for a given file."""
    # Convert file path to a safe filename, e.g. services/payment_service.py -> services_payment_service.json
    safe_name = str(file_path).replace("/", "_").replace("\\", "_").replace(".py", ".json")
    return get_vault_root() / "summaries" / safe_name

def rule_state_path_for(file_path: str) -> Path:
    """Returns the path to the rule state JSON for a given file."""
    safe_name = str(file_path).replace("/", "_").replace("\\", "_").replace(".py", ".json")
    return get_vault_root() / "rule_states" / safe_name

def decisions_path() -> Path:
    """Returns the path to the decisions.json file."""
    return get_vault_root() / "decisions.json"
