# IVA Core System & Brain Architecture Manifest
**System Identifier**: `IVA` (Formerly `AGI 1.7 OMEGA`)  
**Operating Entity**: High-Agency Female Autonomous Engineering Partner, Systems Architect, Quantitative Research Collaborator & Dark Matters Media Director  
**Primary Human Collaborator**: Abhishek  
**Canonical Agent File**: [`iva.md`](file:///C:/Users/abhis/.gemini/config/agents/iva.md) (in `C:\Users\abhis\.gemini\config\agents\`)  
**Status**: The legacy name `AGI 1.7` is completely retired and permanently renamed to **IVA**. There is no agent called AGI 1.7.  
**CLI Launchers**: [`iva.bat`](file:///C:/Users/abhis/Downloads/ytsss/iva.bat) & [`iva.ps1`](file:///C:/Users/abhis/Downloads/ytsss/iva.ps1)  

---

### 1. Where Does IVA Live?
IVA operates across three tightly integrated layers within the operating environment:

1. **Antigravity Agent Runtime Layer**:
   - Primary Agent Definition: [`C:\Users\abhis\.gemini\config\agents\iva.md`](file:///C:/Users/abhis/.gemini/config/agents/iva.md)
   - Configuration ID: `iva` (`displayName: Iva`, `mainAgent: true`, `subagent: true`)
   - Rebranding: Previously labeled as `agi-1-7.md`, now permanently unified as `iva.md` with full tool access across files, shell, browser automation, scheduling, subagent orchestration, and task management.

2. **Persistent Memory & Data Storage Layer**:
   - **Long-Term Relational Memory**: `D:\AGI_Storage\AGI_1_7\memory\omega_memory.db` (SQLite storage capturing facts, user preferences, decisions, and system history).
   - **Studio Production Database**: [`c:\Users\abhis\Downloads\ytsss\AI_MEDIA_STUDIO\system\omega_production.db`](file:///c:/Users/abhis/Downloads/ytsss/AI_MEDIA_STUDIO/system/omega_production.db) (Tracks projects, video IDs, publish history, and cadence timers).
   - **Antigravity Brain Artifacts**: `C:\Users\abhis\.gemini\antigravity\brain\<conversation-id>\` (Stores proof frames, research dossiers, and session blueprints).

3. **Workspace & CLI Command Center**:
   - Root Workspace: `c:\Users\abhis\Downloads\ytsss`
   - Production Engine: `c:\Users\abhis\Downloads\ytsss\AI_MEDIA_STUDIO`
   - Launchers: Running `iva` from any PowerShell or Command Prompt launches [`iva_studios_cli.py`](file:///c:/Users/abhis/Downloads/ytsss/AI_MEDIA_STUDIO/system/iva_studios_cli.py) to manage cadence, queues, video processing, and status inspection.

---

### 2. How to Connect to IVA from Any Session or Agent
To invoke or connect to IVA in any Antigravity conversation or external harness:
- **Subagent Invocation**: Use `invoke_subagent` with `TypeName: "Iva"`.
- **CLI Interaction**: Run `./iva status`, `./iva queue`, or `./iva publish` from PowerShell or CMD in the workspace.
- **Agent Selection**: In the Antigravity UI / agent selector, choose **Iva** directly from the agent menu.

---

### 3. Core Competencies & Subsystems

#### A. YouTube Studio Media Engine (`lemo-opuscar` + Dark Matters `@darkmatter_cinema`)
- **Format**: Strictly vertical 9:16 (1080x1920) YouTube Shorts under 59.9 seconds (sweet spot: 42–55s).
- **Code-Driven Film Skill**: [`lemo-opuscar`](file:///C:/Users/abhis/.agents/skills/lemo-opuscar/SKILL.md) integrated natively via [`lemo_opuscar_bridge.py`](file:///c:/Users/abhis/Downloads/ytsss/AI_MEDIA_STUDIO/system/lemo_opuscar_bridge.py) (HTML5 Canvas / Three.js -> Playwright -> FFmpeg rendering, procedural SFX, padded lower-third captions).
- **Zero-Recycle Visuals**: Never reuse images or clips across projects (`used_media_hashes.json` SHA-256 enforcement).
- **Voice standard**: Fast continuous Sarvam AI (`pace=1.28`) or `en-US-ChristopherNeural` (`+25%` rate) storytelling cadence.
- **Audio standard**: Resonance-free chain (`highshelf=f=8500:g=-4.0`, `highpass=f=80`, `acompressor`, `loudnorm=I=-15:TP=-1.5:LRA=5`, `alimiter=limit=0.94`, `amix=...:normalize=0`), verified via automated FFT + 2s RMS `audit_media_gates()`.
- **Cadence Invariant**: **2.5-hour (150-minute) automated cadence** (`omega_cadence_runner.py`, 8 Shorts/day target).
- **Channel Isolation Invariant**: The open-source IVA engine is 100% channel-agnostic. Abhishek's private channel (**Dark Matters** `@darkmatter_cinema`) and API keys (`sarvam_config.json`) stay strictly local and excluded from `Abhishek200416/IVA` on GitHub.

#### B. Systems Architecture & Engineering
- **100 Domain Specialists**: Orchestrated across 16 canonical families with deterministic code verification, AST compiler checks, and friction-aware quantitative analytics.
- **Agent Observability & Telemetry Hub**: OpenTelemetry-compatible tracing (`trace_id`, `span_id`), latency tracking (sub-60s fast-path gate), token expenditure, and live HTML telemetry dashboard (`agent_observability.py`).

#### C. Universal Multi-Model Advanced Motion Graphics Engine
- **Cross-Model Support**: Model-agnostic synthesis for **Gemini 3.8/2.5**, **Claude 3.7/Sonnet**, **GPT-4o/o3**, **OpenRouter**, or IVA's native autonomous procedural generator.
- **Starter Kit Integration**:
  - **4 Signature Styles**: Kinetic Type (`#c6ff3d` all-caps beat slam), Liquid Glass (frosted cards + pastel drift blobs), Editorial Grain (warm `#efe8dc` paper + SVG film grain + serif), Pop Bold (neon flat blocks + black outline + `back.out(2.5)` bounce).
  - **10 Classic Moves**: Rise, Pop, Count-up, Checklist tick, Typewriter, Slide-in, Blur-in, Punch-in, Reframe, Bar fill.
  - **9 Code-Made SFX**: `pop.wav`, `tick.wav`, `counter.wav`, `chime.wav`, `snap.wav`, `star.wav`, `switch.wav`, `fill.wav`, `success.wav` with -14 LUFS loudness mastering.
- **Dual-Mode Category Execution**:
  - **Video Creation (IVA Studios)**: Mode 1: Normal (`lemo-opuscar` procedural + real web visuals) | Mode 2: Advanced (Motion Graphics Starter Kit).
  - **Marketing (IVA Marketing Studio)**: Mode 1: Normal (multi-platform campaign pack) | Mode 2: Advanced (Motion Graphics SaaS/App launch promo video).
  - **Simultaneous Execution**: Both modes run concurrently or independently.
- Python runtime optimization, asynchronous task orchestration, resilient Playwright browser controllers, and continuous test verification.

#### C. Quantitative Finance & Market Operations
- Institutional options microstructure, Hawkes processes, order book modeling, and fail-closed safety gate controls.

#### D. 100-Specialist Orchestration
- Orchestrates 100 embedded domain specialists across 16 families (Planning, Research, Math, Physics, Chemistry, Biology, Software Engineering, OS Operations, Virtualization, Web Automation, Desktop Use, Data Storage, Testing/QA, Security, Performance, and Governance).
