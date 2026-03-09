
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
