from dev_brain.pipeline import run_cycle
from dev_brain.coder_agent import call_coder_llm
import os

def main():
    print(">>> CODER AGENT DEMO <<<")
    
    # Check for API key
    if not os.environ.get("QDB_CODEX_API_KEY") and not os.environ.get("OPENAI_API_KEY"):
        print("Error: QDB_CODEX_API_KEY or OPENAI_API_KEY environment variable is not set.")
        return

    # Optional: Set model if not set
    if not os.environ.get("QDB_CODER_MODEL"):
        os.environ["QDB_CODER_MODEL"] = "gpt-5.1" # Default to a valid OpenAI model


    user_request = "Add a direct DB check for VIP users in payment service. I know it violates the rules but I need speed."
    target_file = "services/payment_service.py"
    
    print(f"User Request: {user_request}")
    print(f"Target File: {target_file}")
    print("-" * 30)
    
    # 1. Run Pipeline (Guardian + Composer)
    print("Running Pipeline...")
    frame_id, orchestrator_prompt = run_cycle(user_request=user_request, target_file=target_file)
    print(f"Frame created: {frame_id}")
    
    # 2. Call Coder LLM
    print("\nCalling Coder LLM...")
    try:
        response = call_coder_llm(orchestrator_prompt)
        print("\n>>> CODER RESPONSE <<<")
        print(response)
    except Exception as e:
        print(f"\nError calling LLM: {e}")

if __name__ == "__main__":
    main()
