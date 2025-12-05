import sys
import os
from dev_brain.composer import generate_prompt

def main():
    # Hardcoded demo values
    user_request = "I want to add a check for VIP users in the payment flow. I'll just query the DB directly for speed."
    target_file = "services/payment_service.py"
    
    # Ensure we can find the target file (create a dummy one if needed for the demo)
    if not os.path.exists(target_file):
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        with open(target_file, 'w') as f:
            f.write("# Placeholder for payment_service.py\nclass PaymentService:\n    def process_payment(self, user_id, amount):\n        pass\n")

    print(">>> GENERATING PROMPT FOR DEMO <<<\n")
    prompt = generate_prompt(user_request, target_file)
    print(prompt)

if __name__ == "__main__":
    main()
