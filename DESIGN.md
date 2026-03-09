# MentorBoxAI Nova: Design Document

---

## 🎯 Purpose & Vision

MentorBoxAI Nova is an AI-powered backend for generating cinematic educational videos using a 6-layer pipeline, **Amazon Nova 2 Lite** (via AWS Bedrock), and Manim CE. The system is built for the Amazon Nova AI Hackathon 2026 under the Multimodal Understanding category.

---

## 🧠 Layered Pipeline Overview

| Layer | Stage | Purpose |
| :--- | :--- | :--- |
| **1** | **Understanding** | Deconstructs topic into scientific key facts and a cinematic script |
| **2** | **Storyboarding** | Maps the script into a multi-scene visual plan (Scene layout, objects, timings) |
| **3** | **Verification** | Validates the plan against technical requirements (No-LaTeX, Screen Bounds, Cognitive Load) |
| **4** | **Code Generation** | Translates the storyboard into Manim Python code using Few-Shot Template logic |
| **5** | **Refinement** | Injects high-end visual treatments (Glowing pulses, particle backgrounds, smooth transitions) |
| **6** | **Validation & Fix** | Performs Static AST checking and a Runtime Smoke Test. If it fails, Nova Reviewer auto-patches the code |

---

## 🏗️ Component Roles & Responsibilities

- **src/app/services/bedrock_client.py**: Amazon Bedrock client using `boto3 converse()` API. IAM role authentication — no API keys. Throttle retry with 30s backoff.
- **src/app/services/pipeline.py**: Main orchestrator for all 6 pipeline layers, manages job flow, integrates Nova LLM calls, validation, and rendering.
- **src/app/services/prompts.py**: Full prompt engineering templates for all 5 layers + CODEGEN_SYSTEM_PROMPT + VALIDATION_PROMPT.
- **src/app/services/few_shot_examples.py**: 7 golden few-shot examples (Vaccine, Respiration, Fusion, SHM, Mitosis, Quadratic, Epic Biology) with topic-routing function.
- **src/app/services/validator.py**: AST-based static analysis, HALLUCINATED_ANIMATIONS auto-fix, runtime smoke test, visual quality scoring.
- **src/app/services/reviewer.py**: Nova 2 Lite-powered code fixer — given an error message, returns corrected Manim code.
- **src/app/api/v1/endpoints.py**: FastAPI endpoints: POST /api/generate, GET /api/status/{job_id}, GET /health.
- **src/app/models/job.py**: Pydantic models (GenerateRequest, JobResponse, StatusResponse).
- **src/app/core/config.py**: Settings class — Nova model ID, AWS region (us-east-1), LLM params, CORS.
- **bedrock_ping_test.py**: Connectivity test — invokes Nova 2 Lite via Bedrock to verify IAM role and region are correct.
- **scripts/start.sh**: Runs Bedrock ping test before starting uvicorn server.
- **scripts/deploy_aws.sh**: Builds Docker image, pushes to ECR, updates ECS service.

---

## 🔑 LLM Configuration

- **Provider**: Amazon Bedrock (`bedrock-runtime`, us-east-1)
- **Model**: `amazon.nova-lite-v1:0` (Nova 2 Lite)
- **Authentication**: EC2 IAM Instance Profile — zero API key management
- **API**: `boto3 client.converse()` — native AWS Messages API
- **Fallback**: 1 retry on ThrottlingException with 30s backoff
- **AWS services used**: Bedrock (LLM), EC2 (hosting + rendering), S3 (video storage, planned)
- **Region**: us-east-1 (N. Virginia) — Nova 2 Lite available here

---

## ✨ Design Principles & Achievements

- **Zero-LaTeX Architecture**: Custom ColorfulScene uses Unicode/Text rendering with advanced styling, making it crash-proof in cloud/local environments.
- **Screen-Safe Layouts**: Text-wrapping caption engine and boundary-checking logic prevent overlapping UI elements.
- **Procedural Visuals**: All visuals are built using Manim primitives for high-resolution scalability.
- **Self-Healing Logic**: Layer 6 detects errors and invokes Nova Reviewer to auto-patch code before user sees it.
- **No Credential Management**: IAM Instance Profile on EC2 grants Bedrock access automatically — no `.env` API keys needed.
- **Information Density**: Each core scene contains 2-3 labeled objects, a transformation/process animation, a concept caption, and at least one exam-relevant fact.
- **NEET/JEE Focused**: Prompts optimized for Indian competitive exam content with exam tips and key ratios.
- **Developer-Friendly**: Modular, testable, and scalable backend structure for rapid extension and CI/CD.

---

## 🏆 Hackathon Alignment

- **Competition**: Amazon Nova AI Hackathon 2026
- **Category**: Multimodal Understanding — text prompt → visual educational video
- **Required technology**: Amazon Nova 2 Lite (Bedrock) — core LLM for all pipeline layers
- Self-healing pipeline ensures zero runtime crashes and rapid iteration.
- Information-dense visuals and screen-safe layouts optimize learning outcomes.

---

## 🔄 Workflow Summary

1. User submits topic via dashboard or API.
2. Nova 2 Lite processes through 6-layer pipeline, each layer adding structure, checks, and enhancements.
3. Manim renders animation at 720p 30fps (optimized for EC2 render time).
4. Validator and Nova reviewer ensure crash-free output.
5. Video served via FastAPI static file endpoint.
---

## 📚 Further Reading
- See UPDATED_ARCHITECTURE.md for system architecture and data flow.
- See requirements.md for technical requirements and hackathon alignment.

---

## License
MIT
