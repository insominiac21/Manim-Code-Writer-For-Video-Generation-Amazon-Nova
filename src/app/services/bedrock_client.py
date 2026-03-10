"""
Amazon Bedrock LLM Client using Amazon Nova 2 Lite.
Drop-in replacement for groq_client.py — exposes the same call_bedrock() interface.

Authentication: IAM role attached to EC2 instance (no API keys needed).
Model: amazon.nova-lite-v1:0 (us-east-1)
"""
import json
import time
import boto3
from botocore.exceptions import ClientError, ReadTimeoutError, EndpointResolutionError
from typing import Optional

NOVA_MODEL_ID = "amazon.nova-pro-v1:0"
NOVA_REGION = "us-east-1"

# Lazy-initialised client — reused across calls to avoid repeated auth overhead.
_bedrock_client = None


def _get_client():
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = boto3.client(
            "bedrock-runtime",
            region_name=NOVA_REGION,
        )
    return _bedrock_client


def call_bedrock(
    prompt: str,
    system_prompt: str = "You are a helpful AI assistant.",
    max_tokens: int = 4096,
    temperature: float = 0.01,
    model: str = None,
) -> str:
    """
    Call Amazon Nova via Bedrock converse API.
    Signature mirrors call_groq() so pipeline.py / reviewer.py need only
    change the import line.

    Retries once on throttling with a 30s backoff.
    """
    model_id = model or NOVA_MODEL_ID
    client = _get_client()

    body = {
        "system": [{"text": system_prompt}],
        "messages": [
            {"role": "user", "content": [{"text": prompt}]}
        ],
        "inferenceConfig": {
            "maxTokens": max_tokens,
            "temperature": temperature,
        },
    }

    for attempt in range(2):
        try:
            response = client.converse(
                modelId=model_id,
                **body,
            )

            # Log token usage for monitoring
            usage = response.get("usage", {})
            print(
                f"[Bedrock] Nova Pro | in={usage.get('inputTokens', '?')} "
                f"out={usage.get('outputTokens', '?')} tokens"
            )

            # Extract text from converse response
            content_blocks = response["output"]["message"]["content"]
            return "".join(block.get("text", "") for block in content_blocks).strip()

        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code == "ThrottlingException" and attempt == 0:
                wait = 30
                print(f"[Bedrock] Throttled — waiting {wait}s before retry...")
                time.sleep(wait)
                continue
            raise RuntimeError(f"[Bedrock] ClientError ({code}): {e}") from e

        except (ReadTimeoutError, EndpointResolutionError) as e:
            if attempt == 0:
                print(f"[Bedrock] Network error, retrying: {e}")
                time.sleep(5)
                continue
            raise RuntimeError(f"[Bedrock] Network error after retry: {e}") from e

    raise RuntimeError("[Bedrock] All attempts failed")
