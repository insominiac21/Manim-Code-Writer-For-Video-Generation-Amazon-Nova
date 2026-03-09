
"""
Amazon Bedrock / Nova 2 Lite connectivity test.
Run on EC2 to verify the IAM role has Bedrock invoke permissions.
No API keys required — authentication is via the EC2 instance profile.
"""
import boto3
from botocore.exceptions import ClientError

MODEL_ID = "amazon.nova-lite-v1:0"
REGION = "us-east-1"

def ping_bedrock():
    print(f"Testing Amazon Bedrock Nova 2 Lite ({MODEL_ID}) in {REGION}...")
    try:
        client = boto3.client("bedrock-runtime", region_name=REGION)
        response = client.converse(
            modelId=MODEL_ID,
            messages=[{"role": "user", "content": [{"text": "Reply with just the word pong."}]}],
            inferenceConfig={"maxTokens": 10, "temperature": 0.0},
        )
        reply = response["output"]["message"]["content"][0]["text"]
        usage = response.get("usage", {})
        print(f"OK Nova 2 Lite responded: {reply.strip()[:80]}")
        print(f"   Tokens: in={usage.get('inputTokens','?')} out={usage.get('outputTokens','?')}")
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "AccessDeniedException":
            print(f"FAIL AccessDenied - check IAM role has bedrock:InvokeModel permission")
        elif code == "ResourceNotFoundException":
            print(f"FAIL Model not found - ensure region is us-east-1")
        else:
            print(f"FAIL ClientError ({code}): {e}")
        raise
    except Exception as e:
        print(f"FAIL Unexpected error: {e}")
        raise
    print("Bedrock ping complete.")

if __name__ == "__main__":
    ping_bedrock()

def ping_groq_keys():
    keys = [
        os.getenv("GROQ_API_KEY1"),
        os.getenv("GROQ_API_KEY2"),
        os.getenv("GROQ_API_KEY3")
    ]
    model = "llama-3.3-70b-versatile"
    test_prompt = "Ping: Respond with 'pong' if you are online."
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers_template = lambda key: {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    for idx, key in enumerate(keys):
        if not key:
            print(f"❌ GROQ_API_KEY{idx+1} not found in .env")
            continue
        print(f"🔑 Testing GROQ_API_KEY{idx+1}...")
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": test_prompt}
            ],
            "max_tokens": 10,
            "temperature": 0.0
        }
        try:
            response = requests.post(url, headers=headers_template(key), json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                reply = data["choices"][0]["message"]["content"]
                print(f"✅ GROQ_API_KEY{idx+1} is valid! Response: {reply.strip()[:80]}")
            elif response.status_code in (401, 403):
                print(f"❌ GROQ_API_KEY{idx+1} is expired or invalid.")
            else:
                print(f"❌ GROQ_API_KEY{idx+1} failed: {response.status_code} {response.text[:100]}")
        except Exception as e:
            print(f"❌ GROQ_API_KEY{idx+1} error: {e}")
    print("\n✅ All GROQ API key tests complete.")
    return None

if __name__ == "__main__":
    ping_groq_keys()
