import sys
from dev_brain.guardian import process_change_event
from dev_brain.vault_io import load_rule_states, get_vault_root

def main():
    print(">>> GUARDIAN ACTIVATED <<<")
    
    user_goal = "Add a direct DB check for VIP users in payment service. I know it violates the rules but I need speed."
    changed_files = ["services/payment_service.py"]
    
    print(f"Event: {user_goal}")
    print(f"Files: {changed_files}")
    
    new_frame_id = process_change_event(user_goal, changed_files)
    
    print(f"\n[SUCCESS] Created Frame: {new_frame_id}")
    print(f"Path: {get_vault_root() / 'frames' / (new_frame_id + '.json')}")
    
    # Show updated rule states
    print("\n>>> UPDATED RULE STATES <<<")
    for fpath in changed_files:
        rs = load_rule_states(fpath)
        if rs:
            print(f"File: {fpath}")
            for entry in rs.rule_states:
                print(f"  Rule: {entry.rule_id}")
                print(f"  Belief: {entry.state_belief}")
                print(f"  Last Frame: {entry.last_updated_frame}")

if __name__ == "__main__":
    main()
