import urllib.request
import json
import sys

def main():
    url = "http://127.0.0.1:8000/run-cycle"
    headers = {'Content-Type': 'application/json'}
    
    # Sample request
    payload = {
        "user_request": "Optimize the database queries in payment service to avoid N+1 problem",
        "target_file": "services/payment_service.py"
    }
    
    data = json.dumps(payload).encode('utf-8')
    
    print(f"Sending request to {url}...")
    print(f"Payload: {payload}")
    
    try:
        req = urllib.request.Request(url, data, headers)
        with urllib.request.urlopen(req) as response:
            result = json.load(response)
            
        print("\n>>> RESPONSE <<<")
        print(f"Frame ID: {result.get('frame_id')}")
        print("-" * 20)
        print("Generated Prompt (preview):")
        print("-" * 20)
        print(result.get('prompt'))
        
    except urllib.error.URLError as e:
        print(f"\nError: Could not connect to server. Is it running on port 8000? ({e})")
        print("Make sure you started the server with: python -m dev_brain.cli_server")

if __name__ == "__main__":
    main()
