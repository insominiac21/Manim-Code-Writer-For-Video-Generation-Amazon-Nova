
# MentorBoxAI Nova: AI Educational Video Engine (Amazon Nova Edition)

MentorBoxAI converts any topic into a 3Blue1Brown-style educational animation using a 6-layer AI pipeline powered by **Amazon Nova 2 Lite** on AWS Bedrock. Type a concept, get a rendered MP4 — no animation experience needed.

**Built for:** Amazon Nova AI Hackathon 2026 — Multimodal Understanding category

**Stack:** FastAPI · Amazon Bedrock (Nova 2 Lite) · Manim CE v0.19 · AWS EC2 (Ubuntu, us-east-1)

---

## AWS Services

| Service | How it's used |
| :--- | :--- |
| **Amazon Bedrock — Nova 2 Lite** | Powers all 6 pipeline layers: topic understanding, storyboarding, code generation, verification, and self-healing auto-fix. Accessed via IAM role — no API keys required. |
| **EC2** (us-east-1) | Hosts the FastAPI server (port 8000) and runs the Manim renderer. Manim requires Linux (Cairo, Pango, ffmpeg) — EC2 Ubuntu 22.04 provides this cleanly. IAM instance profile grants Bedrock access. |
| **S3** (mentorbocai-nova-videos) | Configured for video upload and CDN delivery. Planned for next release. |
| **DynamoDB** | Configured for persistent job history. Planned for next release. |

### Why EC2 and not Lambda?
Manim render jobs take 60–180 seconds and require persistent filesystem access (writing `.py` files, reading back `.mp4`). Lambda's 15-minute limit and ephemeral `/tmp` are unsuitable. EC2 gives full control over the rendering environment.

### Why Amazon Nova 2 Lite?
- **Native AWS integration:** IAM role auth — zero credential management
- **Price-performance:** Frontier reasoning at a fraction of GPT-4 cost
- **Bedrock converse API:** Clean Messages-style interface with structured system prompts
- **Hackathon fit:** Multimodal Understanding track — text prompt → visual educational video

---

## Key Features
- **6-Layer AI Pipeline:** Understanding → Storyboarding → Verification → Code Generation → Refinement → Validation & Auto-Fix
- **Amazon Nova 2 Lite (Bedrock):** Single IAM-role authenticated client, no key rotation complexity
- **Zero-LaTeX:** All visuals use `Text()` — crash-proof on any Linux server, no TeX installation needed
- **22 Template Helpers:** Pre-built `ColorfulScene` methods the LLM calls directly (phasor animation, particle physics, energy charts, collision bursts, layout zones)
- **Golden Few-Shot Examples:** NEET/JEE quality examples for biology, physics, chemistry, and maths
- **Self-Healing:** AST static check → subprocess smoke test → Nova-powered auto-patch before the user sees any error
- **720p Output:** All renders at `-qm` (1280×720 30fps), 180s timeout

---

## 🏗️ Project Structure
```
github-ready/
├── src/
│   └── app/
│       ├── api/v1/endpoints.py       # FastAPI endpoints
│       ├── models/job.py             # Pydantic models
│       ├── services/
│       │   ├── groq_client.py        # Groq API client with key rotation
│       │   ├── pipeline.py           # 6-layer pipeline logic
│       │   ├── prompts.py            # All prompt templates (L1-L5 + system)
│       │   ├── few_shot_examples.py  # Golden few-shot examples (NEET quality)
│       │   ├── validator.py          # AST static analysis + runtime smoke test
│       │   └── reviewer.py          # Groq-powered auto-fix for validation errors
│       ├── core/config.py           # Settings (Groq keys, AWS, LLM params)
│       ├── main.py                  # FastAPI app entry
│       └── __init__.py
├── .env.example                     # Groq + AWS config template
├── Dockerfile                       # Production container (python:3.11-slim + ffmpeg)
├── README.md                        # Project documentation
├── requirements.txt                 # Python dependencies
├── bedrock_ping_test.py             # Groq key + AWS service connectivity check
├── scripts/
│   ├── start.sh                     # Server startup (validates keys first)
│   └── deploy_aws.sh               # ECR build + ECS deploy
├── output/
│   ├── manim/                       # Generated Manim scripts
│   └── videos/                      # Rendered MP4 files
└── frontend/                        # Dashboard UI
```

---

## 🧠 The 6-Layer Pipeline
| Layer | Stage | Purpose |
| :--- | :--- | :--- |
| **1** | **Understanding** | Deconstructs topic into key facts and cinematic script |
| **2** | **Storyboarding** | Maps script into visual plan (scenes, objects, timings) |
| **3** | **Verification** | Validates plan against technical and pedagogical constraints |
| **4** | **Code Generation** | Translates storyboard into Manim Python code using few-shot templates |
| **5** | **Refinement** | Enhances visuals with effects and quality improvements |
| **6** | **Validation & Fix** | Static and runtime validation, auto-patching for crash-free output |

---

## ✨ System Architecture
```
User Input (Topic, Duration)
		 │
		 ▼
┌─────────────────┐
│  Layer 1:       │
│  Understanding  │──→ understanding.json
└────────┬────────┘
		 │
		 ▼
┌─────────────────┐
│  Layer 2:       │
│  Storyboarding  │──→ plan.json
└────────┬────────┘
		 │
		 ▼
┌─────────────────┐
│  Layer 3:       │
│  Verification   │──→ verified_plan.json
└────────┬────────┘
		 │
		 ▼
┌─────────────────┐
│  Layer 4:       │
│  Code Generation│──→ scene.py (draft)
└────────┬────────┘
		 │
		 ▼
┌─────────────────┐
│  Layer 5:       │
│  Refinement     │──→ scene.py (enhanced)
└────────┬────────┘
		 │
		 ▼
┌─────────────────┐
│  Layer 6:       │
│  Validation     │──→ scene.py (final)
└────────┬────────┘
		 │
		 ▼
┌─────────────────┐
│  Manim Render   │──→ video.mp4
└─────────────────┘
```

---

## Getting Started

### 1. Prerequisites
- Python 3.10+
- Manim Community Edition v0.19+ with ffmpeg and sox (**Linux/WSL only** for rendering)
- Groq API key (free at [console.groq.com](https://console.groq.com))
- AWS account for EC2 deployment (optional for local dev)

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Configuration
Copy `.env.example` to `.env` and fill in:
```env
GROQ_API_KEY1=gsk_...
GROQ_API_KEY2=gsk_...   # optional, for rate-limit rotation
GROQ_API_KEY3=gsk_...   # optional
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET=mentorbocai-videos
```

### 4. Launch (EC2 / Linux)
```bash
cd /home/ubuntu/app
venv/bin/uvicorn src.app.main:app --host 0.0.0.0 --port 8000
```

### 4. Launch (local dev — Windows, no rendering)
```powershell
.\run-local.ps1
```
Open [http://localhost:8000](http://localhost:8000)

> **Note:** Manim rendering only works on Linux. On Windows, code generation and pipeline layers work, but the render step will fail unless you have WSL with Manim installed.

---

## Generating a Video

```bash
curl -X POST http://<EC2_IP>:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"concept":"simple harmonic motion","goal":"explain for JEE","duration_seconds":60,"max_scenes":5,"auto_render":true}'
```

Poll for completion:
```bash
curl http://<EC2_IP>:8000/api/status/<job_id>
```

---

## LLM: Groq (not AWS Bedrock)
All LLM calls go through **Groq** (`llama-3.3-70b-versatile`), not AWS Bedrock. Groq was chosen for:
- **~10× lower latency** than Bedrock for this model size
- Free tier sufficient for development and demo
- Simple REST API with Python SDK

The client (`groq_client.py`) rotates across up to 3 API keys to avoid per-key rate limits during heavy pipeline runs.

---

## Troubleshooting
| Issue | Solution |
|-------|----------|
| `NameError` / `ImportError` in render | Validator auto-fixes most issues. Re-run generation. |
| Video too short | Increase `duration_seconds` |
| Text overflow / overlap | Title max 25 chars, captions auto-wrapped at 40 chars |
| Render fails | Must run on Linux (EC2/WSL). Windows render is not supported. |
| Groq rate limit | Add a second/third API key to `.env` as `GROQ_API_KEY2`, `GROQ_API_KEY3` |
| EC2 port 8000 unreachable | Check Security Group inbound rule: TCP 8000, source 0.0.0.0/0 |

---

## Further Reading
- [UPDATED_ARCHITECTURE.md](UPDATED_ARCHITECTURE.md) — full pipeline and component map
- [docs/design.md](docs/) — hackathon design rationale
- [docs/requirements.md](docs/) — feature requirements

---

## License
MIT
