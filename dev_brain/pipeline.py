from typing import List, Optional, Tuple
from . import guardian, composer

def run_cycle(
    user_request: str,
    target_file: str,
    changed_files: Optional[List[str]] = None
) -> Tuple[str, str]:
    """
    High-level orchestration:
    1. Run the Guardian/Archivist on this change event to update the vault.
    2. Generate a governance-aware prompt for the Coding LLM.

    - user_request: natural language description of the dev intent.
    - target_file: path to the main file being edited.
    - changed_files: list of files touched; if None, default to [target_file].

    Returns:
        (frame_id, prompt_text)
    """
    if changed_files is None:
        changed_files = [target_file]
        
    # 1. Run Guardian
    frame_id = guardian.process_change_event(
        user_goal=user_request,
        changed_files=changed_files
    )
    
    # 2. Run Composer
    prompt_text = composer.generate_prompt(
        user_request=user_request,
        target_file=target_file
    )
    
    return frame_id, prompt_text
