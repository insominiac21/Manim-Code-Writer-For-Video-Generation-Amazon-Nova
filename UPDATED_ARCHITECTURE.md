
# MentorBoxAI: System Architecture

---

## Overview

MentorBoxAI transforms any topic into a 3Blue1Brown-style educational animation using a 6-layer AI pipeline. The system runs on **AWS EC2 (Ubuntu, us-east-1 N. Virginia)** for all compute and rendering, uses **Amazon Nova 2 Lite** (via Amazon Bedrock) for LLM inference, and **Manim Community Edition v0.19** for video rendering.

---

## AWS Services Used

| Service | Role | Status |
| :--- | :--- | :--- |
| **EC2** (t3.medium, us-east-1) | Runs the FastAPI server + Manim renderer. All code generation, AST validation, and MP4 rendering happens here. The instance is the backbone of the entire system. | **Active** |
| **S3** (bucket: mentorbocai-videos) | Configured for video storage and CDN delivery. Credentials are wired in `.env`. | **Configured, not yet wired** |
| **DynamoDB** | Planned for persistent job history and user session storage. Credentials are wired in config. | **Configured, not yet wired** |
| **Amazon Bedrock** | Hosts **Amazon Nova 2 Lite** (`amazon.nova-lite-v1:0`) — the LLM powering all 6 pipeline layers. Authentication via IAM role (no API keys). | **Active** |

### Why EC2 specifically?
Manim requires **Cairo, Pango, ffmpeg, and sox** — all Linux-native. Windows support is fragile. EC2 (Ubuntu 22.04) provides a clean, reproducible Manim rendering environment without WSL complexity. The FastAPI server runs inside a Python venv at `/home/ubuntu/app/venv/`.

### Request flow
```
User Browser / API Client
    │
    │  HTTP POST /api/generate
    ▼
┌──────────────────────────────────────────┐
│          AWS EC2 (us-east-1)             │
│  Ubuntu 22.04 · port 8000                │
│                                          │
│  ┌─────────────────────────────────┐     │
│  │  FastAPI (uvicorn)              │     │
│  │  src/app/main.py                │     │
│  └──────────────┬──────────────────┘     │
│                 │                        │
│  ┌──────────────▼──────────────────┐     │
│  │  6-Layer Pipeline               │     │
│  │  pipeline.py                    │     │
│  │                                 │     │
│  │  L1: Understanding  ──────────────────────→ Amazon Bedrock (Nova 2 Lite)
│  │  L2: Storyboarding  ──────────────────────→ Amazon Bedrock (Nova 2 Lite)
│  │  L3: Verification   ──────────────────────→ Amazon Bedrock (Nova 2 Lite)
│  │  L4: Code Gen       ──────────────────────→ Amazon Bedrock (Nova 2 Lite)
│  │  L5: Refinement     ──────────────────────→ Amazon Bedrock (Nova 2 Lite)
│  │  L6: Validate & Fix ──────────────────────→ Amazon Bedrock (Nova 2 Lite)
│  └──────────────┬──────────────────┘     │
│                 │                        │
│  ┌──────────────▼──────────────────┐     │
│  │  Manim CE v0.19 Renderer        │     │
│  │  /home/ubuntu/app/venv/bin/manim│     │
│  │  → output/videos/*.mp4          │     │
│  └──────────────┬──────────────────┘     │
│                 │                        │
└─────────────────┼────────────────────────┘
                  │
                  │  HTTP 200 · { video_url, job_id }
                  ▼
           User browser
```

---

---

## The 6-Layer Pipeline

| Layer | Stage | What the LLM does | Output |
| :--- | :--- | :--- | :--- |
| **1** | **Understanding** | Extracts key facts, formulas, NEET/JEE exam tips from the topic | `understanding.json` |
| **2** | **Storyboarding** | Designs scene sequence: objects, positions, transitions, timings | `plan.json` |
| **3** | **Verification** | Checks plan for screen-bound violations, LaTeX usage, cognitive overload | `verified_plan.json` |
| **4** | **Code Generation** | Writes Manim Python using few-shot golden examples + 22 template helpers | `scene.py` (draft) |
| **5** | **Refinement** | Adds glow effects, particle background, caption polish | `scene.py` (enhanced) |
| **6** | **Validation & Fix** | AST static check → runtime smoke test → LLM reviewer auto-patches failures | `scene.py` (final) |

---

## Component Map

| File | Role |
| :--- | :--- |
| `src/app/services/pipeline.py` | Orchestrates all 6 layers, manages async job state, calls Manim subprocess |
| `src/app/services/manim_templates.py` | `ColorfulScene` base class: 3-layer starfield, 22+ animation helpers (phasor, particles, collision, energy chart, layout zones) |
| `src/app/services/prompts.py` | All LLM prompt templates for L1–L5 + code generation system prompt with 22 method catalogue and 17 cinematic patterns |
| `src/app/services/few_shot_examples.py` | Golden few-shot examples (vaccine, star lifecycle, cellular respiration, nuclear fusion, SHM phasor) |
| `src/app/services/validator.py` | AST static analysis: detects banned calls, bad scales, screen-overflow, then runtime smoke test |
| `src/app/services/reviewer.py` | Nova 2 Lite-powered auto-fix: given validator error, rewrites the broken snippet |
| `src/app/services/bedrock_client.py` | Amazon Bedrock client with Nova 2 Lite via `converse()` API, IAM role auth, throttle retry |
| `src/app/api/v1/endpoints.py` | FastAPI REST endpoints: `POST /api/generate`, `GET /api/status/{id}`, `GET /health` |
| `src/app/core/config.py` | Settings: Nova model ID, AWS region, S3 bucket, Manim path |
| `src/app/models/job.py` | Pydantic request/response models |
| `output/manim/` | Generated `.py` Manim scripts |
| `output/videos/` | Rendered `.mp4` files served via `/videos/{file}` |
| `frontend/` | Vanilla JS dashboard: topic form, job polling, video preview |

---

## Manim Template Helpers (ColorfulScene)

`ColorfulScene` is the base class every generated scene inherits from. It provides:

**Background:** 3-layer deep-space starfield (60 static stars, 20 drifting nebula particles, 5 twinkling stars)

**Layout helpers:** `clamp_to_screen`, `safe_next_to`, `arrange_column`, `stack_labels` — prevent overlap

**Animation helpers:**
- `phasor_to_sine_animation()` — 3B1B-style rotating phasor traces live sine wave
- `static_sine_wave()` — frozen FunctionGraph with label
- `collision_burst()` — Flash + shock rings for A+B→C reactions
- `show_energy_diagram()` — animated bar chart (ATP yield, etc.)
- `create_particle_group()` + `animate_particles_movement()` — physics particle cloud
- `create_glowing_object()`, `add_glow_pulse()`, `add_fun_pulse()`
- `show_title()`, `play_caption()`, `setup_gradient_header()`
- `create_reaction_arrow()`, `add_transformation_arrow()`, `animate_process()`

---

## Design Principles

- **Zero-LaTeX:** All text uses `Text()` — no LaTeX dependency, crash-proof on any Linux server
- **Screen-safe layouts:** Hard-clamped Y zones (TITLE / UPPER / CENTER / LOWER / CAPTION) enforced at prompt and validator level
- **Self-healing:** Layer 6 runs AST check → subprocess smoke test → Nova 2 Lite reviewer auto-patch before the user ever sees an error
- **LLM-safe helpers:** Complex animations (`ValueTracker`, `always_redraw`, `ParametricFunction`) are pre-built as single-call template methods — the LLM just calls `self.phasor_to_sine_animation()`, not the internals
- **1080p output:** All renders use `-qh` (1920×1080) with 240s timeout
- **NEET/JEE focused:** Prompts include exam tips, key ratios, and topic-specific few-shot examples (biology, physics, chemistry, maths)

---

## License
MIT
