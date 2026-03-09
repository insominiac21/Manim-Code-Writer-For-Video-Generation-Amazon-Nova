"""
MentorBoxAI - Application Configuration
All settings are loaded from environment variables / .env file.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # App
    APP_NAME: str = "MentorBoxAI"
    VERSION: str = "4.0.0"
    ENV: str = os.getenv("NODE_ENV", "development")
    PORT: int = int(os.getenv("PORT", 8000))
    CORS_ORIGIN: str = os.getenv("CORS_ORIGIN", "*")

    # Amazon Bedrock — Nova 2 Lite
    NOVA_MODEL_ID: str = os.getenv("NOVA_MODEL_ID", "amazon.nova-lite-v1:0")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    LLM_GENERATOR_MAX_TOKENS: int = int(os.getenv("LLM_GENERATOR_MAX_TOKENS", "4096"))
    LLM_GENERATOR_TEMPERATURE: float = float(os.getenv("LLM_GENERATOR_TEMPERATURE", "0.01"))

    # AWS (S3, DynamoDB — credentials via IAM role on EC2, no keys needed)
    S3_BUCKET: str = os.getenv("S3_BUCKET", "mentorbocai-nova-videos")

    # Storage
    BASE_DIR: str = os.getenv("BASE_DIR", "")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "output")

settings = Settings()
