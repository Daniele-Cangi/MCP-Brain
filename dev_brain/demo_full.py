from dev_brain.pipeline import run_cycle

def main():
    print(">>> FULL PIPELINE DEMO <<<")
    
    user_request = "Add a direct DB check for VIP users in payment service. I know it violates the rules but I need speed."
    target_file = "services/payment_service.py"
    
    print(f"User Request: {user_request}")
    print(f"Target File: {target_file}")
    print("-" * 30)
    
    frame_id, prompt = run_cycle(user_request=user_request, target_file=target_file)
    
    print(f"\nFrame created: {frame_id}")
    print("\n--- PROMPT TO SEND TO LLM ---")
    print(prompt)

if __name__ == "__main__":
    main()
