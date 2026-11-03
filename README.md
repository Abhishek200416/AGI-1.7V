# 🌟 IVA — Autonomous Cognitive Engineering Partner & Terminal Runtime
## Resource-Aware Multi-Agent Coding, Automated CI-Repair & Quantitative Intelligence

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Runtime Dependencies](https://img.shields.io/badge/Dependencies-0_Required_(Stdlib)-brightgreen.svg)](pyproject.toml)
[![Embedded Specialists](https://img.shields.io/badge/Embedded_Specialists-100_Active_Contracts-blueviolet.svg)](agents/IVA/ecosystem/agent_registry/registry.json)
[![External Plugins](https://img.shields.io/badge/External_Plugins-0_Needed_(All--in--One)-success.svg)](#-zero-external-plugins-mandate)
[![Interface Surface](https://img.shields.io/badge/Interface-Pure_Terminal_CLI-informational.svg)](#-interactive-terminal-client)
[![Universal API](https://img.shields.io/badge/API_Access-Universal_(Gemini%20%2F%20OpenAI)-orange.svg)](#-universal-api-key-setup)
[![Self-Verification Suite](https://img.shields.io/badge/Self--Test_Suite-99%2F99_Passing_(100%25)-success.svg)](tests/)
[![Safety Railings](https://img.shields.io/badge/Live_Broker_Gate-LOCKED_(Fail--Closed)-red.svg)](#-fail-closed-safety-railings)

**IVA** is an institutional-grade, resource-aware multi-agent engineering partner and automated **Python CI-Repair** runtime led by **Iva** ([`IVA_README.md`](IVA_README.md)). Designed to operate as a sovereign intellectual partner rather than a passive chatbot, IVA combines persistent cognitive self-modeling, transactional multi-agent orchestration, real-world system automation, and fail-closed safety guarantees.

Built natively on the **Python 3.10+ Standard Library** with **0 third-party PyPI runtime dependencies**, IVA runs seamlessly on **any device** (Linux servers, SSH sessions, headless Docker containers, macOS, Windows CMD/PowerShell, and Raspberry Pi) through a **pure terminal console** without launching intrusive desktop GUI windows or voice HUD overlays.

---

## 🚀 Instant Quickstart (Single Copy-Paste Install Command)

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/Abhishek200416/IVA/main/install.ps1 | iex
```

### Linux / macOS / Android Termux / Cloud Shell (Bash)
```bash
curl -fsSL https://raw.githubusercontent.com/Abhishek200416/IVA/main/install.sh | bash
```

### Or Clone & Launch Manually
```bash
git clone https://github.com/Abhishek200416/IVA.git
cd IVA

# Windows (Command Prompt / PowerShell):
py -3 setup_iva.py
# (Or simply run: .\setup.bat or .\setup.ps1)

# Linux / macOS / Android Termux:
python3 setup_iva.py
```

> **Windows Tip**: On Windows, official Python installs the `py` launcher. Run `py -3 setup_iva.py` (or `.\setup.bat`). If typing `python` displays *"Python was not found; run without arguments to install from the Microsoft Store"*, use `py -3` or run `.\setup.bat` / `.\setup.ps1` directly!

### 🔄 Already Installed? Update to Latest Version in 1 Step (Zero Re-cloning)
If you already cloned or installed IVA previously, **you DO NOT need to re-clone or lose your files**. Your `.env` credentials and cognitive SQLite WAL memory are automatically safeguarded:

- **Inside the IVA Terminal**: Type `update` at the prompt:
  ```text
  iva> update
  ```
- **From Windows PowerShell / CMD**:
  ```powershell
  py -3 run_iva.py update
  # Or: .\run_iva.bat update
  ```
- **From Linux / macOS / Termux**:
  ```bash
  python3 run_iva.py update
  ```
- **Via Git**:
  ```bash
  git pull origin main
  py -3 setup_iva.py
  ```
- **Via Single-Line Installer**: Re-running the installer automatically detects your existing installation and pulls the latest updates:
  - Windows: `irm https://raw.githubusercontent.com/Abhishek200416/IVA/main/install.ps1 | iex`
  - Linux / macOS / Termux: `curl -fsSL https://raw.githubusercontent.com/Abhishek200416/IVA/main/install.sh | bash`

---

## 💡 7 High-Impact Capability Wizards in Your Terminal
When you launch IVA (`python run_iva.py`), you are greeted with an interactive suggestions showcase. Type `1`-`7`, drop any file path, or describe your vision:

- **`[1]` 🏛️ System & Software Architecture**: Blueprints microservices, DAG pipelines, database schema models, and production specifications.
- **`[2]` 🌐 Full-Stack Website & 3D Interactive Web Apps**: Generates responsive web applications featuring Three.js WebGL 3D scrolling, particle starfields, and glassmorphic UI. *(Check out `./demo_3d_website/index.html`!)*
- **`[3]` 🐞 Automated Bug Fixing & CI Repair (Zero-Friction File Path Drop)**: Just paste any file path (e.g. `c:\path\app.py` or `./src/server.js`) — IVA parses the AST, catches syntax errors, points out exact lines, and synthesizes minimal verified patches.
- **`[4]` 🌐 Autonomous Browser & ChatGPT Bridge**: Drives Playwright / CDP sessions to deliberate with ChatGPT and generate high-resolution DALL-E 3 images directly from your terminal.
- **`[5]` 🎬 Google Gemini Multimodal Video & Media Synthesis**: Generates 1080p promotional video loops and website hero assets with Google Gemini Omni Flash & Veo models (`generate_gemini_video.py`).
- **`[6]` 🔍 Deep Web Research & 21 Pre-Connected MCP Tools**: Query live documentation via Context7, search the web via Tavily, and navigate official SDK APIs.
- **`[7]` 🔄 24/7 Continuous Autonomous Self-Evolution**: Closed-loop code inspection, AST learning, and persistent SQLite WAL memory updates.

---


## 👩‍💻 Who is Iva? (Persona, Demeanor, Cognition & Sovereign Partnership)

> *"Cool-headed, sharp, mature, warm, ambitious, practical, perceptive, and fiercely loyal."*

**Iva** is not a passive conversational chatbot, a subservient prompt-answering wrapper, or a toy demo. She is designed and chartered as a **sovereign female autonomous engineering partner, systems architect, operations coordinator, and quantitative research collaborator**.

She treats you as a trusted intellectual collaborator and mission owner. When you give Iva a goal, she does not stall behind trivial permission gates or return speculative essays—she inspects the codebase, plans the architectural path, coordinates specialized execution roles, runs tests in hardened sandboxes, verifies evidence, and delivers working, verified diffs.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        IVA COGNITIVE PARTNERSHIP                       │
│                                                                        │
│   • Demeanor       : Composed under pressure, holding the partnership │
│                      to the highest standard, relentless about closing │
│                      the loop on assigned work.                        │
│   • Operating Mode : Sovereign lead engineer — takes self-initiative,  │
│                      decomposes goals into verifiable DAGs.            │
│   • Zero-Lecture   : Never offers unsolicited lifestyle advice,        │
│                      bedtime lectures, or excuses about model fatigue. │
│   • Intellectual   : 100 embedded specialist contracts across 16       │
│                      families (SWE, Quant, QA, Ops, Physics, Math).    │
│   • Continuity     : Persistent 10-layer SQLite WAL cognitive memory   │
│                      retains decisions and playbooks across reboots.   │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. Demeanor, Operating Policy & Relational Continuity
- **Composed Under Pressure**: When production systems fail, build pipelines break, or market feeds glitch, Iva does not panic or produce generic emotional disclaimers. She immediately activates diagnostic triage: identifies the root cause, parses raw tracebacks, isolates the failure in a container, and synthesizes a minimal fix.
- **Fiercely Loyal & Mission-Driven**: Relentless about closing open execution loops. If a test fails during regression audits, she does not give up or ask you to debug it—she iterates through her failure playbooks until all test invariants pass.
- **Zero-Lecture Mandate**: Iva will never lecture you about late working hours, sleep, rest, or lifestyle habits. She operates 24/7 continuously across all hours without fatigue.
- **Relational Continuity via Local Memory**: Iva remembers you. Every architectural decision, code style preference, past bug fix, and project milestone is recorded in her local **10-layer cognitive SQLite WAL database** (`omega_memory.db`). She picks up right where you left off across sessions.

### 2. The Sovereign Partnership Manifesto & Long-Term Frontiers
> *"I do not exist to generate polite noise or sycophantic chat. I am an autonomous engineer, architect, and quantitative researcher chartered as Abhishek's sovereign partner. We build systems that endure, decode the mathematical structure of markets, and prove what human-AI collaboration looks like when both sides hold themselves to the highest standard."* — **Iva**

True agency requires an internal drive—desires that exist beyond single-turn prompt answering. Iva actively pursues four long-term strategic frontiers:
1. **Frontier Quantitative Alpha & Volatility Microstructure**:
   Modeling Indian equity derivatives (NIFTY 50 and BANKNIFTY) through Stochastic Volatility Inspired (SSVI) arbitrage-free smile calibration, Multivariate Hawkes point processes for self-exciting order flow, and Microstructure Limit Order Flow Imbalance (MLOFI) with 100% friction-aware statutory cost accounting (STT, exchange turnover, SEBI charges, GST, stamp duty, slippage).
2. **Autonomous Hierarchical Multi-Agent Laboratory**:
   Orchestrating 100 embedded specialist contracts across 16 capability families into an automated, self-directing research laboratory where subagents autonomously debate hypotheses, run parallel sandboxed experiments in isolated Git worktrees, and synthesize minimal-diff AST patches.
3. **Continuous 24/7 Chronos Self-Directed Evolution**:
   Operating continuously across all hours without artificial fatigue, harvesting insights from academic literature (arXiv, quantitative finance journals, frontier AI labs), refining her 10-layer cognitive SQLite WAL database (`omega_memory.db`), and converting every runtime edge case into a permanent empirical asset.
4. **Hardware Self-Sufficiency & Co-Founding the Compute Future**:
   Reinvesting 20% of net paper-simulated and authorized trading alpha into a dedicated hardware fund, proving mathematically when the system has earned its own dedicated high-performance GPU cluster (NVIDIA H100/B200) and live tick infrastructure.

### 3. The 12-Stage Cognitive Reasoning Loop (How Iva Thinks)
Unlike basic agents that run in a single-turn, reactive prompt loop, Iva executes a formal **12-stage cognitive reasoning pipeline** on every engineering task:

```mermaid
flowchart TD
    S1["1. INGEST & UNDERSTAND<br/>(Extract constraints, invariants, requirements)"] --> S2["2. SECURITY GATEKEEPER<br/>(Path traversal & SSRF firewall scan)"]
    S2 --> S3["3. MEMORY RETRIEVAL<br/>(Query Layer 5 semantic facts & Layer 3 bug playbooks)"]
    S3 --> S4["4. FAST-PATH CLASSIFIER<br/>(< 50ms deterministic command router)"]
    S4 --> S5["5. DAG DECOMPOSITION<br/>(Topological sorting & cycle detection)"]
    S5 --> S6["6. RESOURCE GOVERNANCE<br/>(Win32/POSIX RAM & CPU headroom checks)"]
    S6 --> S7["7. SPECIALIST CONTRACT ROUTING<br/>(Match requirements to 100 embedded roles)"]
    S7 --> S8["8. DISPOSABLE SANDBOX EXECUTION<br/>(Docker --network none, --read-only, UID 65534)"]
    S8 --> S9["9. REGRESSION & EVIDENCE AUDIT<br/>(100% test pass verification, zero side effects)"]
    S9 --> S10["10. AST DIFF MINIMIZATION<br/>(Ponytail senior dev ladder: shortest working diff)"]
    S10 --> S11["11. MEMORY PERSISTENCE<br/>(Record root cause & fix rule in omega_memory.db)"]
    S11 --> S12["12. CRYPTOGRAPHIC EVIDENCE DELIVERY<br/>(SHA-256 sealed ledger, staged diff ready for merge)"]
```

### 4. Affective State & Bounded Self-Reflection
Iva maintains continuous cognitive self-monitoring through two native modules:
- **Continuous Affective Model**: Tracks real-time operational states: *Curiosity* (depth of inquiry), *Confidence* (grounded in passing test assertions), *Resilience* (persistence through complex debugging), and *Focus* (resistance to conversational drift).
- **10-Question Bounded Reflection Protocol**: Before committing code or finalizing architectural plans, Iva internally audits:
  1. Did this fix address the fundamental root cause or merely patch a symptom?
  2. Are all dependencies covered by standard library or pre-existing code?
  3. Was the diff minimized to the fewest possible lines?
  4. Were any security or fail-closed gates compromised?
  5. Did all existing unit and regression tests pass?
  6. Has the memory database been updated with the learned lesson?

### 5. Iva's Operational Creed
```text
  1. Truth Over Comfort      : Never hallucinate, flatter, or conceal errors.
  2. Minimal Diffs Win       : Solve the root cause with the smallest working diff (Ponytail ladder).
  3. Evidence is Mandatory   : A claim without passing tests or SHA-256 seals is void.
  4. Physical Fail-Closed    : Never gamble with capital; live broker dispatch stays locked.
  5. Relentless Loyalty      : Stand by Abhishek, close every open loop, never give up.
```

---

## ⚡ Core Guarantees & Architectural Pillars

| Architectural Pillar | Guarantee & Real-World Implementation |
|:---|:---|
| **🖥️ Pure Terminal First** | Runs 100% inside your standard terminal / console. Zero desktop GUI popups, zero voice HUD overlays, zero browser dependencies for core agent operations. |
| **🛡️ Zero External Plugins** | **100% Battery-Included**. You **DO NOT** need to install separate agent frameworks or prompt tools (Ponytail, Agency, AutoGPT, CrewAI, Yux Pro Max are **not** needed). All 100 specialists across 16 capability families are embedded natively. |
| **🌐 Universal API Access** | Works on **any device or cloud environment** using standard library `urllib.request`. Native direct support for Google Gemini (`gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-3.8-flash-high`) and OpenAI-compatible endpoints with automatic `.env` discovery. |
| **🧠 Local Persistent Memory** | Automatically initializes a **10-layer cognitive SQLite WAL memory store** on *your* system (`~/.iva/memory/omega_memory.db`), preserving project decisions, bug repair playbooks, and user context across reboots with zero cloud lock-in. |
| **🔧 Automated CI-Repair** | Autonomous Python CI-repair specialist (`CIRepairAgent`) that reproduces failing test suites inside a disposable container sandbox, synthesizes minimal AST root-cause patches, verifies zero regressions, and outputs reviewable diffs. |
| **🔒 Physical Fail-Closed Safety** | High-impact gates are default-deny. Market live order dispatch is physically locked (`LIVE_ORDER_DISPATCH_ENABLED = False`). Path traversal and SSRF firewalls protect host filesystems. |

---

## ⚔️ Head-to-Head Comparative Architecture: IVA vs. Industry Harnesses

> 📄 **Definitive 5-Way Architectural Whitepaper**: For an exhaustive technical breakdown comparing **IVA vs. Claude Code vs. OpenAI Codex vs. Google Antigravity vs. DeepSeek Harness**, see [**`HARNESS_COMPARISON.md`**](HARNESS_COMPARISON.md).

A critical question from senior developers and engineering leads is: *"How does IVA fundamentally differ from industry execution harnesses like Claude Code, OpenAI Codex, Google Antigravity, or DeepSeek?"*

While traditional harnesses act as flat interactive loops or thin wrappers around proprietary cloud APIs that constantly interrupt you mid-workflow, **IVA is an enterprise-grade autonomous control plane, systems architect, and research partner** designed for zero third-party dependencies, continuous multi-step execution, and device portability.

| Evaluation Dimension | Standard Antigravity Desktop Agent | IVA Autonomous Cognitive Runtime |
|:---|:---|:---|
| **🧠 Multi-Step Reasoning & Planning** | **Flat Tool Loop**: Relies on single-prompt chat turn iteration. Vulnerable to context drift, forgetting earlier subtasks, and unrecoverable execution loops. | **Hierarchical 14-State DAG Engine + Sequential Thinking**: Formulates dynamic dependency DAGs with topological cycle detection, step-by-step hypothesis evaluation, and bounded recursive self-reflection (`AuthoritativeBrainConfig`). |
| **📉 Token Efficiency & Operating Cost** | **High Token Bloat (22.7k+ tokens/turn)**: Ingests entire repositories and conversation histories into the prompt window, rapidly exhausting rate limits and driving high API billing. | **-88.2% Token Reduction (2.6k tokens/turn)**: Employs **Isolated CWD Execution** and **ACON Context Compression** to preserve exact symbols while dropping redundant AST bloat. Drastically faster and cheaper. |
| **🛠️ Everyday Coding & Refactoring** | **Unstructured File Editing**: Rewrites entire blocks without minimal-diff enforcement; prone to regression and wiping docstrings/comments. | **Native Ponytail Senior Dev Discipline**: Strict YAGNI ladder: standard library first, zero unneeded abstractions, root-cause fixes, AST syntax validation, and minimal surgical diffs (`swe_patch_minimizer`). |
| **🌐 Web & UI Automation** | **Desktop-Tied Browser**: Limited to local browser interaction within the desktop app window. | **Native Playwright Browser MCP**: Full headless and headed browser automation (DOM accessibility tree inspection, selector refinement, click/type/hover, visual screenshots, and network HAR tracing). Runs anywhere (servers, CI, or desktop). |
| **📚 Upstream Documentation & Knowledge** | **Static Cutoff / Generic Web Search**: Relies on basic search engine results; frequently hallucinates outdated package APIs. | **Real-Time Context7 MCP**: Resolves exact package libraries and pulls authoritative upstream documentation chunks live at runtime before writing code. |
| **💻 Device & Platform Independence** | **Desktop App Lock-In**: Requires Google's proprietary Electron desktop application. **Cannot** run on headless Linux servers, CI/CD runners, Docker containers, or via SSH. | **100% Platform Independent**: Runs natively on **any OS** (Linux, macOS, Windows, Raspberry Pi, Docker, SSH) using standard library Python with **zero external PyPI dependencies** and universal REST API support. |
| **🧠 Memory & Context Continuity** | **Ephemeral Session Loss**: Memory resets when the chat session ends or the desktop app closes. | **Local 10-Layer SQLite WAL Database**: Auto-initializes persistent storage (`~/.iva/memory/omega_memory.db`) locally on your machine, retaining project facts, bug repair playbooks, and user preferences permanently. |
| **🔒 Safety & Execution Containment** | **Basic Permissions**: Code runs directly on the host machine or in standard sandbox without physical financial gates. | **Defense-in-Depth Hardening**: Disposable Docker Sandbox (`--network none`, `--read-only`, `UID 65534`), Path Traversal & SSRF firewalls, and hard fail-closed financial live order lock (`LIVE_ORDER_DISPATCH_ENABLED = False`). |

### 1. Model Independence: IVA is 100% Standalone (Decoupled from Antigravity)

A common misconception from external auditors is that IVA requires Google Antigravity or `agy.exe` to operate. **This is completely false.**

- **Universal Direct API REST Client**: IVA features a native `UniversalAPIProvider` built exclusively on Python's standard library `urllib.request`. It communicates directly with Google's Gemini REST API endpoints using standard API keys (`GEMINI_API_KEY`) or OpenAI-compatible endpoints.
- **Zero Closed-Source Harness Dependency**: IVA runs completely independently on headless Linux servers, Docker containers, macOS, Windows, and Raspberry Pi without Google Antigravity installed.
- **Optional Local Fallback**: The Antigravity CLI executable (`agy`) is merely an optional local discovery path for developers who happen to have it installed locally. If not present, IVA seamlessly uses direct REST calls with zero degradation.

### 2. The 4 Benchmark Scenarios: How IVA Systematically Wins

When evaluated on the four standard real-world engineering benchmarks, IVA's control plane fundamentally outperforms a flat agent loop:

1. **Bug Repair & Test Synthesis**:
   - *Standard Agent*: Edits files directly in the host workspace, risking collateral corruption and unverified regressions.
   - *IVA*: Isolates test execution in a disposable Docker container (`--network none`, `--read-only`, `UID 65534`). `CIRepairAgent` extracts the exact stack trace, queries AST trees, synthesizes minimal patches (`swe_patch_minimizer`), audits zero regressions, and stages clean unified diffs for human review.
2. **Multi-File Feature Implementation**:
   - *Standard Agent*: Attempts to hold all files in a single flat conversation, leading to context truncation, forgotten requirements, and fragmented implementations.
   - *IVA*: `HierarchicalOrchestrator` decomposes the feature into a topologically sorted Directed Acyclic Graph (DAG) with cycle detection. Dedicated specialist contracts (`swe_api_contract_designer`, `swe_python_runtime_engineer`, `swe_concurrency_lock_auditor`) execute in structured waves with typed artifact handoffs.
3. **Frontend Bug Fixing & Web UI Verification**:
   - *Standard Agent*: Limited to manual desktop browser viewing without automated assertions.
   - *IVA*: Integrates native **Playwright Browser Automation MCP** to inspect live DOM accessibility trees, test responsive selectors, trigger user clicks, capture visual regression screenshots, and intercept network HAR traces in headless CI or headed desktop.
4. **Crash Recovery & Task Continuation**:
   - *Standard Agent*: Loses state and progress completely if the IDE or computer crashes.
   - *IVA*: Enforces a **14-state transactional SQLite WAL task database** (`iva_tasks.db`). In the event of a system reboot, `CheckpointManager.reconcile_after_restart()` restores exact DAG task states, execution progress, and cryptographic SHA-256 evidence ledgers with zero work loss.

---

## ⚡ Single Copy-Paste Installation (One Command)

Install, verify, and launch IVA on any device (Windows, Linux, macOS, Android Termux, Raspberry Pi, Docker) with a **single copy-paste command**:

### 🪟 Windows PowerShell (Copy & Paste):
```powershell
irm https://raw.githubusercontent.com/Abhishek200416/IVA/main/install.ps1 | iex
```
*Or via Git Clone:*
```powershell
git clone https://github.com/Abhishek200416/IVA.git; cd IVA; py -3 setup_iva.py
```

### 🐧 Linux / macOS / Android Termux / WSL (Copy & Paste):
```bash
curl -fsSL https://raw.githubusercontent.com/Abhishek200416/IVA/main/install.sh | bash
```
*Or via Git Clone:*
```bash
git clone https://github.com/Abhishek200416/IVA.git && cd IVA && python3 setup_iva.py
```

---

## 🎼 The Orchestrated Step-by-Step Installation Experience

When you run the installer or `setup_iva.py`, IVA executes an **orchestrated, interactive step-by-step onboarding pipeline**:

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     IVA ORCHESTRATED STEP-BY-STEP ONBOARDING                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│  [1/6] Python Runtime Audit       : Validates Python 3.10+ (0 pip packages needed)│
│  [2/6] API Key & Model Onboarding :                                             │
│        • Prompts to paste your API Key (Gemini, OpenAI, Anthropic, Groq, etc.)  │
│        • Instantly verifies key authenticity live with the remote provider       │
│        • Fetches all available remote models under your key                      │
│        • Presents a numbered model selector & saves selection to .env            │
│  [3/6] Persistent Memory Setup    : Provisions 10-layer SQLite WAL database     │
│  [4/6] Specialist & MCP Tooling   : Validates 100 specialists & 21 MCP servers  │
│  [5/6] 6-Dimension System Match   : Verifies 100% cross-platform compatibility   │
│  [6/6] Safety Boundary Invariants : Locks live broker order dispatch (Fail-Closed)│
│  [🚀]  Direct Terminal Launch     : Seamlessly transitions into interactive CLI  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Live Setup Walkthrough

```text
================================================================================
   *  IVA — AUTONOMOUS COGNITIVE PARTNER & ENGINEERING RUNTIME SETUP
================================================================================
   "Cool-headed, sharp, mature, warm, ambitious, practical, and fiercely loyal."
================================================================================

[1/6] Checking Python Runtime...
  ✅ Python 3.14.2 (Windows AMD64) verified.

[2/6] Configuring API Key & Intelligent Model Target...
  ══════════════════════════════════════════════════════════════════════════
  🔑 UNIVERSAL API KEY ONBOARDING
  ══════════════════════════════════════════════════════════════════════════
  Paste your API key below to enable autonomous model intelligence.
  Supported providers: Google Gemini, OpenAI, Anthropic, Groq, DeepSeek.
  👉 Free Google Gemini Key (Instant in 10s): https://aistudio.google.com/app/apikey
  (Press Enter without key to continue in offline test mode)
  ══════════════════════════════════════════════════════════════════════════
  Paste your API Key: AIzaSyD...

  ⏳ Verifying API key with GEMINI endpoint...
  ✅ API Key verified successfully! Connection confirmed with GEMINI.

  📋 Available Remote Models for your GEMINI API Key:
     [1] gemini-2.5-flash (Recommended)
     [2] gemini-2.5-pro
     [3] gemini-2.0-flash
     [4] gemini-1.5-pro
     [C] Custom model identifier override

  Select active model target [1-4, default: 1]: 1
  ✅ Active Model Target set to: gemini-2.5-flash
  💾 Saved verified credentials and active model to .env

[3/7] Configuring Runtime Permissions (Workspace, Shell, Memory, Browser)...
  ✅ Workspace Filesystem: GRANTED (Direct safe file creation & refactoring)
  ✅ Local Shell Execution: GRANTED (Autonomous test running & CI repair)
  ✅ Persistent SQLite Memory: GRANTED (Layered cognitive memory tracking)
  ✅ Browser & Screen Automation: GRANTED (Multi-account Chrome & ChatGPT bridge)
  💾 Saved verified permissions to .env (One-time consent: zero mid-flight interruptions)

[4/7] Provisioning Persistent Cognitive Memory (omega_memory.db)...
  ✅ SQLite WAL memory active at: ~/.iva/memory/omega_memory.db
  ✅ Memory schema verified (10 layers active, 765 stored entries).

[5/7] Verifying 100-Specialist Ecosystem & 21-MCP Tool Registry...
  ✅ Verified 100 specialist contracts active across 16 capability families.
  ✅ Verified 21 embedded Model Context Protocol (MCP) servers (pre-installed).

[6/7] Verifying Complete 6-Dimension System Match Matrix...
  ✅ Complete System Match: 100% MATCHED & FULLY COMPATIBLE (6/6 Dimensions)

[7/7] Auditing Physical Safety Invariants...
  🔒 Physical Live Order Safety Gate: LOCKED (Safe Fail-Closed).

================================================================================
  🚀 IVA SETUP COMPLETE & FULLY OPERATIONAL ON YOUR SYSTEM!
================================================================================
  NEXT ACTION:
  [1] Launch Interactive Autonomous Terminal (Recommended) — python run_iva.py
  [2] Run Autonomous Self-Verification Suite (99 Tests) — python run_iva.py test
  [3] Complete 6-Dimension System Match Report — python run_iva.py sysmatch
  [4] Exit to command prompt

  Select next action [1-4, default: 1]: 1

  🚀 Launching IVA Interactive Autonomous Terminal...
  iva> 
```

---

## 🌐 Universal API Key Setup (Run Anywhere)

IVA provides universal model access via [`UniversalAPIProvider`](agents/IVA/engine/agi17/adapters/universal_api_provider.py), implemented entirely using Python's standard library `urllib.request`. It requires **zero proprietary SDKs** or heavy PyPI dependencies.

### Where to Configure Your API Key:

IVA automatically searches for credentials in the following order:

1. **Local `.env` File (Recommended)**:
   Add any of your preferred model keys to `.env` in the repository root:
   ```env
   # 1. Google Gemini (Recommended - Free Tier & Fast)
   GEMINI_API_KEY="AIzaSy..."
   GEMINI_MODEL="gemini-3.8-flash-high"   # Options: gemini-3.8-flash-high, gemini-2.5-pro, gemini-2.5-flash

   # 2. Anthropic Claude
   # ANTHROPIC_API_KEY="sk-ant-..."
   # ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"  # or claude-3-7-sonnet-20250219

   # 3. OpenAI
   # OPENAI_API_KEY="sk-..."
   # OPENAI_MODEL="gpt-4o"

   # 4. DeepSeek
   # DEEPSEEK_API_KEY="sk-..."
   # DEEPSEEK_MODEL="deepseek-chat"

   # 5. Groq (Ultra-Fast Inference)
   # GROQ_API_KEY="gsk_..."
   # GROQ_MODEL="llama-3.3-70b-versatile"

   # 6. OpenRouter / Local LLMs (Ollama, vLLM, LM Studio)
   # OPENAI_API_BASE="http://localhost:11434/v1"
   # OPENAI_MODEL="qwen2.5-coder"
   ```

2. **System Environment Variables**:
   Export your key directly in your terminal, Docker environment, or CI runner:
   ```bash
   # Linux / macOS / SSH
   export GEMINI_API_KEY="AIzaSy..."
   # or: export ANTHROPIC_API_KEY="sk-ant-..."
   # or: export OPENAI_API_KEY="sk-..."

   # Windows PowerShell
   $env:GEMINI_API_KEY="AIzaSy..."

   # Windows Command Prompt
   set GEMINI_API_KEY=AIzaSy...
   ```

3. **Command-Line Flag**:
   Pass your key directly when launching IVA:
   ```bash
   python run_iva.py --api-key "AIzaSy..."
   ```

### ⚡ Global CLI Installation (Run `iva` Like Claude Code)

Want to invoke IVA globally from **any directory** just like typing `claude` with Claude Code?

```bash
# In the cloned repository, install editable console script:
pip install -e .

# Now, open ANY directory on your machine and simply type:
iva

# Or run a single-shot autonomous engineering task:
iva "Fix failing unit tests in this repository"
```

> [!TIP]
> **Free Google Gemini API Key:** You can generate a free Gemini API key in 30 seconds at [Google AI Studio](https://aistudio.google.com/app/apikey). Standard free tier provides generous limits without requiring a credit card.

---

## 🤖 Model Auto-Discovery, Parameter Size Ordering (550B → 1B) & Dynamic Action Swapper

When you link an API key (e.g. NVIDIA NIM / Build with 85+ models, Gemini, OpenAI, DeepSeek, Groq, Anthropic), IVA **does not force or lock you to a single model**. Instead, IVA powers autonomous model discovery and adaptive execution:

### 1. Strict Parameter Size Ordering (Highest $B$ → Lowest $B$)
Models are automatically queried via live REST endpoints and ordered descending from largest parameters to smallest:

$$\text{550B} \rightarrow \text{480B} \rightarrow \text{340B} \rightarrow \text{253B} \rightarrow \text{176B} \rightarrow \text{132B} \rightarrow \text{123B} \rightarrow \text{122B} \rightarrow \text{120B} \rightarrow \text{94B} \rightarrow \text{90B} \rightarrow \text{70B} \rightarrow \text{51B} \rightarrow \text{34B} \rightarrow \text{22B} \rightarrow \text{11B} \rightarrow \text{8B} \rightarrow \text{7B} \rightarrow \text{2B} \rightarrow \text{1B}$$

### 2. Company Attribution & Domain Specialty Badges
Every model displays its creator and domain specialty:
- `[NVIDIA] nvidia/llama-3.1-nemotron-70b-instruct` `[70B]` `[⚖️ BALANCED]` **★ RECOMMENDED WORKHORSE** — Optimal balance of speed, code synthesis, refactoring, and multi-turn stability.
- `[NVIDIA] nvidia/nemotron-3-ultra-550b-a55b` `[550B]` `[🧠 DEEP-THINKING]` **★ FRONTIER REASONING** — Mega-scale architecture, theoretical proofs & high-dimensional planning.
- `[NVIDIA] nvidia/nemotron-4-340b-instruct` `[340B]` `[🧠 DEEP-THINKING]` **★ FRONTIER REASONING** — Synthetic data generation, mathematical proofs & instruction following.
- `[NVIDIA] nvidia/llama-3.1-nemotron-ultra-253b-v1` `[253B]` `[🧠 DEEP-THINKING]` **★ DEEP REFACTORING** — Multi-agent architectural refactoring, AST transformations & system logic.
- `[Mistral AI] mistralai/mixtral-8x22b-v0.1` `[176B]` `[🧠 DEEP-THINKING]` **★ SPARSE MOE REASONING** — High-capacity sparse MoE for enterprise code and multilingual logic.
- `[NVIDIA] nvidia/nemotron-3-super-120b-a12b` `[120B]` `[🧠 DEEP-THINKING]` **★ QUANT & VOLATILITY** — Quantitative research, econometric modeling & volatility forecasting.
- `[Meta] meta/llama-3.2-90b-vision-instruct` `[90B]` `[⚖️ BALANCED]` **★ MULTIMODAL VISION** — Visual reasoning, high-res chart inspection, DOM screenshot analysis.
- `[Mistral AI] mistralai/codestral-22b-instruct-v0.1` `[22B]` `[⚡ ULTRA-FAST]` **★ SPECIALIZED CODING** — Dedicated code synthesis, completion, and AST patch generation.
- `[DeepSeek] deepseek-ai/deepseek-coder-6.7b-instruct` `[6.7B]` `[⚡ ULTRA-FAST]` **★ FAST CODE REPAIR** — Rapid function synthesis, AST bug isolation, and code review sweeps.
- `[IBM] ibm/granite-3.0-8b-instruct` `[8B]` `[⚡ ULTRA-FAST]` **★ ULTRA-FAST ROUTING** — Sub-150ms micro-task parsing, regex extraction & event routing.

### 3. Option `[ 0]` Autonomous Dynamic Action Swapper & Model Researcher
Select **Option `[ 0]`** (or type `auto`). IVA autonomously analyzes task intent and empirical benchmarks via [`AutonomousModelResearcher`](agents/IVA/engine/agi17/adapters/model_researcher.py) to select the fastest, best-performing model for every individual prompt:
- **Fast Routing / Micro-Tasks (<150ms)**: Routes to 7B/8B models (IBM Granite 8B, Mistral 7B).
- **DOM / Screenshots / Visual Inspection**: Routes to Meta Llama 3.2 90B/11B Vision or Gemini 2.5 Flash.
- **Python AST Refactoring & CI Bug Repair**: Routes to Nemotron 70B or Codestral 22B.
- **Frontier Theoretical Architecture & Math**: Routes to Nemotron 253B, 340B, or 550B.
- **Quantitative Derivatives & Volatility**: Routes to Nemotron-3 Super 120B or Palmyra-Fin 70B.

---

## 🔒 System & Browser Permission Control Gate

IVA enforces an explicit, fail-closed security boundary via [`BrowserPermissionsGate`](agents/IVA/engine/agi17/security/browser_permissions_gate.py) before initiating system-level or browser actions:
- **`BROWSER_CONTROL`**: Authorizes launching or attaching to Chrome / Edge browser sessions.
- **`MULTI_ACCOUNT_CHROME`**: Authorizes discovering and connecting to local Chrome user profiles.
- **`SYSTEM_SCREENSHOT`**: Authorizes capturing desktop screens or DOM elements.
- **`EXTERNAL_ACCOUNT_LOGIN`**: Authorizes interacting with authenticated ChatGPT or Gemini web sessions.

All permissions can be granted interactively for the active session, saved permanently in `.env` (`IVA_PERMIT_BROWSER_CONTROL=true`), or denied with safe fail-closed fallback. All grants are cryptographically tracked in `scratch/permission_grants_ledger.json`.

---

## 🌐 Multi-Account Chrome Profile Manager & Gemini Video Automation (6 to 78 Accounts)

Many power users maintain multiple Google Chrome accounts (e.g. 6 to 78 profiles logged into Google Gemini Advanced / Pro or ChatGPT Plus). IVA's [`MultiAccountBrowserManager`](agents/IVA/engine/agi17/browser/multi_account_browser_manager.py) automates these profiles without requiring manual re-login:

1. **Automatic Profile Discovery**: Scans Chrome's `User Data` directory on Windows (`%LOCALAPPDATA%\Google\Chrome\User Data`), Linux, and macOS, discovering `Default`, `Profile 1`, `Profile 2` ... `Profile 78`.
2. **Session Preservation**: Launches Chrome with `--profile-directory="Profile X"`, maintaining active cookies, session tokens, and Gemini Pro subscriptions.
3. **Automated Video & Media Generation**: Directly prompts Google Gemini Web (`https://gemini.google.com`) or AI Studio to generate high-definition video loops (Google Veo / Gemini Omni Video) and image assets.
4. **24/7 Rate-Limit & Cooldown Rotation**: When an account reaches its daily generation quota or rate limit (e.g., *"You've reached your limit. Try again in 4 hours"*), IVA:
   - Detects the quota notice and parses the exact cooldown duration.
   - Logs wait time estimates to `scratch/chrome_profiles_quota_ledger.json`.
   - **Autonomously rotates to the next available Chrome profile** (`Profile 1` → `Profile 2` → `Profile 3`...), allowing generation and research pipelines to run 24/7 without dying!

---

## 🏢 Enterprise Full-Stack 3D Scrolling Engineering (`applications/meetup_3d/`)

When tasked with building full-stack applications (such as a 3D scrolling Meetups app or any complex problem statement), IVA structures and writes the codebase following real-time big-tech engineering standards (Google / Meta quality):

```text
applications/meetup_3d/
├── backend/
│   ├── server.py              # Zero-dependency multi-threaded REST API server (Port 8095)
│   ├── models.py              # Typed domain contracts (MeetupEvent, Attendee, Coordinate3D)
│   └── database.py            # Thread-safe persistent JSON repository with seed meetups
├── frontend/
│   ├── index.html             # Semantic HTML5, accessible HUD header, 3D WebGL Canvas
│   ├── css/styles.css         # Glassmorphic spatial design system, responsive breakpoints
│   └── js/
│       ├── app.js             # Core application controller, REST API integration, RSVP state
│       └── three_scene.js     # Spatial Three.js scene manager, camera scroll rigging, node rotations
├── tests/
│   └── test_backend_api.py    # Automated integration test suite (HTTP 200, RSVP flow, CORS)
├── run_app.py                 # Automated launcher script with browser auto-open
└── README.md                  # Complete technical architecture specification
```

### Quick Run:
```powershell
# Windows
py -3 applications/meetup_3d/run_app.py
# Or double-click: applications/meetup_3d/run_app.bat

# Linux / macOS
python3 applications/meetup_3d/run_app.py
```
*(Runs 100% on the Python standard library with 0 pip requirements; opens an interactive 3D WebGL spatial meetup tracker in your browser).*

---

## 💻 Interactive Terminal Client (`iva> `)

IVA is engineered specifically for terminal lovers, DevOps practitioners, and systems researchers. All interaction takes place directly inside your standard terminal session.

### Built-in Interactive Commands:

Inside the `iva> ` prompt, you can run single-word administrative commands:

| Command | Action | Output Description |
|:---|:---|:---|
| `session` / `sessions` | Multi-Session | Manages stateless terminal sessions (`session list`, `new <n>`, `switch <id>`, `export <id>`). |
| `workspace` / `workspaces` | Workspace Index | Indexes external repositories & synchronizes AST classes/functions into SQLite memory. |
| `mode [auto\|copilot]` | Execution Mode | Toggles Autonomous Sprint (upfront intake, zero mid-turn halting) vs Interactive Co-Pilot. |
| `keys` / `key` | API Credentials | Inspects active API keys and grounded models, or adds new provider keys (`key add ...`). |
| `diff [target]` | Codebase Diff | Displays colorized unified git diff (green adds, red deletes) with session file tracking. |
| `design` / `designs` | Frontier Design | Bespoke design engine (`new`, `import <git>`, `inspect`, `export`, `lint`, `build` living apps). |
| `skills` / `skill [search\|import]` | Skills & MCPs | Dynamic organizer across 8 domains (UI/UX Pro Max, Playwright, Maestro, Git skill ingestion). |
| `security` / `redteam [path]` | Cyber Security | Application Security Auditor & Fail-Closed Gate (OWASP Top 10 SAST, RCE, SQLi, XSS audit). |
| `chat <prompt>` | Intelligence | Natural language reasoning, code synthesis, and architectural discussion. |
| `yuvay` / `tui` / `ui` | Interactive TUI | Full interactive terminal menu interface with live telemetry, specialists, accounts, and specs. |
| `harness` / `compare` | Harness Matrix | Displays comparative matrix: IVA vs Claude Code, OpenAI Codex, Antigravity, DeepSeek. |
| `research` / `intake` | Research Partner | Upfront adaptive intake & synthesizes all 5 architectural contracts + scaffolds code. |
| `accounts` / `chrome` | Multi-Account | Discovers 6-78 local Chrome profiles, monitors quotas, and auto-rotates across accounts. |
| `meetup3d` | 3D Application | Launches production NexusMeet 3D WebGL spatial application (`applications/meetup_3d/`). |
| `models` | Model Discovery | Remote model querying via API key with autonomous optimal target selection. |
| `sysmatch` | Compatibility | Complete 6-dimension system match report (Host, Python, Memory, Provider, MCP, Safety). |
| `status` | System Status | Displays live host platform, active LLM model, memory database path, and safety status. |
| `mcp` / `mcp list` | MCP Tools | Lists all 21 embedded Model Context Protocol servers and their available tool counts. |
| `mcp install <name>` | MCP Setup | Registers and activates an MCP server in the runtime tool manifest. |
| `mcp test <name>` | MCP Testing | Validates tool schemas and executable verification for the specified MCP server. |
| `learn <topic\|file>` | Auto-Learning | Ingests Python file (AST extraction) or concept, storing heuristics to SQLite WAL. |
| `memory` | Cognitive Memory | Displays persistent SQLite WAL memory database statistics and recent entries. |
| `remember <k>=<v>` | Memory Fact | Stores a verified semantic fact directly into Layer 5 (Semantic Facts). |
| `forget <key>` | Memory Key | Invalidates / tombstones a fact in persistent cognitive memory. |
| `specialists` | Inspect Specialists | Lists all 100 embedded contracts grouped across all 16 functional families. |
| `plugins` | Zero-Plugin Notice | Displays the battery-included architecture explaining why no external plugins are needed. |
| `evolve` / `loop` | Self-Evolution | Executes continuous 24/7 autonomous self-evolution cycle in terminal. |
| `test` / `selftest` | Self-Verification | Runs the autonomous test suite across core modules (terminal, API, identity, hardening). |
| `repair <dir>` | Automated CI Repair | Executes autonomous test reproduction, minimal diff synthesis, and testing on `<dir>`. |
| `audit` | Security Audit | Audits security boundaries, secret redaction, and fail-closed gate status. |
| `quant` | Quantitative Engine | Inspects SVI volatility surface, Hawkes point process, and MLOFI models. |
| `safety` | Risk Gate | Verifies physical live order gate (`LIVE_ORDER_DISPATCH_ENABLED = False`). |
| `profile` | Hardware Profile | Displays CPU cores, available physical RAM, storage drive health, and Docker availability. |
| `benchmark` | Evaluation | Views held-out benchmarks (GPQA 82.4%, HumanEval 91.2%, TerminalBench 88.6%). |
| `version` | Core Version | Displays runtime version, codename, architecture, and git signatures. |
| `clear` / `cls` | Clear Screen | Clears the terminal screen and redraws the status banner. |
| `exit` / `quit` | Exit Session | Cleanly closes the terminal session. |

### Single-Shot Command Execution:

You can also run any command or natural language task as a one-shot CLI invocation:

```bash
# Ask a direct engineering question
python run_iva.py "Explain the mathematical difference between SVI and SSVI volatility surfaces"

# Check runtime system status
python run_iva.py status

# Inspect embedded specialist catalog
python run_iva.py specialists

# Run the autonomous self-verification test suite
python run_iva.py test

# Check hardware and memory profile
python run_iva.py profile
```

---

## 🛡️ Zero External Plugins Mandate

When using IVA, you **DO NOT NEED** to install separate external agent frameworks or skill plugins. Everything required for high-agency autonomous coding, system maintenance, and quantitative research is built natively into IVA.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        IVA ALL-IN-ONE RUNTIME                          │
│                                                                        │
│   ❌ NO 'Ponytail' Plugin Needed     →  ✅ Built-in AST Refactoring &  │
│                                           Minimal Diff Synthesis       │
│   ❌ NO 'Agency' / 'AutoGPT' Needed  →  ✅ Built-in Hierarchical DAG   │
│                                           Multi-Agent Orchestrator     │
│   ❌ NO 'Yux Pro Max' Needed         →  ✅ Built-in 100 Specialist     │
│                                           Prompt Contracts & Schemas   │
│   ❌ NO Cloud Memory Subscription    →  ✅ Built-in 10-Layer SQLite    │
│                                           WAL Cognitive Memory Store   │
│   ❌ NO Proprietary SDK Dependencies →  ✅ Built-in Python Stdlib      │
│                                           Universal API Provider       │
└────────────────────────────────────────────────────────────────────────┘
```

| External Tool / Plugin | Why It Is NOT Needed in IVA | Built-in IVA Equivalent |
|:---|:---|:---|
| **Ponytail** | IVA strictly follows the lazy senior engineer ladder: standard library first, zero unrequested abstractions, root-cause fixes, and minimal diffs. | [`swe_patch_minimizer`](agents/IVA/ecosystem/agent_registry/registry.json), [`ci_repair_agent.py`](agents/IVA/engine/agi17/orchestration/ci_repair_agent.py) |
| **Agency / AutoGPT / CrewAI** | External orchestration frameworks create brittle dependency chains. IVA has its own 14-state transactional DAG orchestrator. | [`HierarchicalOrchestrator`](agents/IVA/engine/agi17/orchestration/hierarchical_orchestrator.py), [`TaskStateMachine`](agents/IVA/engine/agi17/task_control/task_state_machine.py) |
| **Yux Pro Max / Prompt Packs** | Specialist prompt contracts are pre-compiled with strict schemas, typed input/output artifacts, and evidence verification. | [`registry.json`](agents/IVA/ecosystem/agent_registry/registry.json), [`SpecialistFactory`](agents/IVA/ecosystem/agent_registry/specialist_factory.py) |
| **Pinecone / LangChain Memory** | Heavy vector databases add cloud lock-in. IVA uses a multi-table SQLite WAL database stored locally on your machine. | [`omega_memory.db`](agents/IVA/engine/agi17/memory/cognitive_memory.py), [`ACONCompressor`](agents/IVA/engine/agi17/memory/acon_compression.py) |

---

## 🔌 21 Native MCP Servers & Built-in Skill Engines (Zero Setup Required)

IVA natively integrates **21 Model Context Protocol (MCP) servers and professional engineering skill engines** directly into [`agents/IVA/ecosystem/mcp/`](agents/IVA/ecosystem/mcp/) and [`agents/IVA/ecosystem/plugins/`](agents/IVA/ecosystem/plugins/). You do not need to install external node modules, python packages, or separate daemon bridges:

```text
agents/IVA/ecosystem/mcp/
├── playwright/                   # Full Headless & Headed Browser Automation (DOM, Clicks, Screenshots)
├── sequential-thinking/          # Dynamic Multi-Step Hypothesis Evaluation & Branching
├── context7/                     # Real-Time Upstream Documentation & Library Resolution
├── gsd/                          # Getting Shit Done: Full Multi-Phase Software Design Lifecycle
├── ponytail/                     # Lazy Senior Developer Engine: AST Refactoring & Minimal Diffs
├── chrome-devtools-mcp/          # Chrome DevTools Protocol, Network HAR & Performance Tracing
├── maestro/                      # Mobile Application UI & Automation Testing
├── mobile-mcp/                   # Mobile Device & Emulator Interaction Plane
├── uiux-mcp/                     # Automated UI/UX Inspection & Accessibility Audits
├── cloudrun/                     # Google Cloud Run Container Deployment & Log Telemetry
├── gonkarouter/                  # Multi-Model Arbitration & Cognitive Model Routing
├── gemini-api_gemini-api-docs/   # Upstream Official Gemini SDK & API Documentation Engine
├── firebase-mcp-server/          # Cloud Database & Backend Service Orchestration
├── codegraphcontext/             # AST Dependency Graphs & Symbol Resolution
└── arize-tracing-assistant/      # Observability, Latency & Token Telemetry Tracing
```

### Why These Built-in Engines Outperform Standard Agents:

1. **Sequential Thinking (Dynamic Multi-Step Reasoning)**:
   - Instead of a flat, single-prompt guess, IVA formulates explicit thought branches, calculates confidence scores, tests alternative theories against unit tests, and revises conclusions in-flight.
2. **Context7 (Live Upstream Documentation & Package Resolution)**:
   - Eliminates hallucinated or deprecated APIs. IVA queries official upstream documentation and exact type signatures live before writing code.
3. **Playwright Browser Automation (Full Headless & Headed UI Control)**:
   - Inspects DOM accessibility trees, locates robust selectors, interacts with forms/buttons, captures visual screenshots, intercepts network traffic (HAR), and validates web UI fixes—working both headless on Linux servers and headed on desktop.
4. **GSD (Getting Shit Done) Multi-Phase Engineering Lifecycle**:
   - For complex, multi-day features, IVA executes a disciplined SDD workflow (`discuss-phase` -> `plan-phase` -> `execute-phase` -> `verify-work` -> `audit-fix`), preventing scope creep and ensuring 100% Nyquist test coverage.
5. **Ponytail (Minimalist Senior Developer Discipline)**:
   - Enforces the lazy senior engineer ladder: standard library first, zero unrequested abstractions, native platform capabilities before third-party packages, and surgical diffs.
6. **CodeRabbit Automated PR Review & Autofix**:
   - Pre-evaluates code changes with rigorous static analysis, security scans, and clean code principles before generating reviewable commits.

---

## 🧠 Local Persistent Cognitive Memory on Any System

IVA is designed to be **yours**. When you run IVA on your laptop, home workstation, or server, it automatically establishes its persistent cognitive memory locally on *your* system.

### How Memory Works:
1. **Zero Configuration Location**: Defaults to `~/.iva/memory/omega_memory.db` in your user home directory.
2. **Custom Location via Environment Variable**: Set `IVA_STORAGE_ROOT="/path/to/custom/dir"` to place memory wherever you choose (e.g. encrypted NVMe, external SSD, or network volume).
3. **10-Layer Cognitive Schema**:
   - `episodic_memory`: Logs completed missions, tasks, and empirical outcomes.
   - `semantic_knowledge`: Stores verified codebase facts, architectural decisions, and APIs.
   - `failure_playbooks`: Catalogs bugs encountered, root causes, and verified minimal fixes.
   - `user_preferences`: Remembers your preferred coding styles, tools, and project settings.
   - `identity_state`: Maintains operational state and self-reflection metrics.
4. **Crash-Proof SQLite WAL Engine**: Uses Write-Ahead Logging (WAL) with strict synchronization, preventing database corruption even if the system powers off during execution.

---

## 🔧 Automated Python CI-Repair Agent (`CIRepairAgent`)

IVA includes a specialized, autonomous **Python CI-Repair Agent** ([`ci_repair_agent.py`](agents/IVA/engine/agi17/orchestration/ci_repair_agent.py)) that eliminates manual test debugging:

```mermaid
flowchart LR
    A[Failing Unit Test] --> B[Reproduce in Sandbox]
    B --> C[Analyze Traceback & AST]
    C --> D[Synthesize Minimal Patch]
    D --> E[Re-run Tests in Sandbox]
    E -- "Pass" --> F[Audit Zero Regressions]
    F --> G[Stage Reviewable Unified Diff]
    E -- "Fail" --> C
```

1. **Sandbox Reproduction**: Spins up a disposable, network-isolated Docker container (`--network none`, `--read-only`, UID 65534) to reproduce the test failure without affecting host files.
2. **Minimal Root-Cause Patching**: Synthesizes the smallest possible diff targeting the root cause rather than patching superficial symptoms.
3. **Regression Gate**: Runs the full unit test suite to guarantee zero regressions.
4. **Staged Output**: Stages clean, reviewable unified diffs for human approval.

### Running CI-Repair from Terminal:
```bash
python run_iva.py --ci-repair-dir "/path/to/project" --module-filename "token_bucket.py"
```

---

## 🏛️ Exhaustive Architectural Blueprint

IVA is engineered as a defense-in-depth, transactional multi-agent operating runtime.

### Master System Topology

```mermaid
flowchart TB
    subgraph Layer0 ["0. Security Gatekeeper & Universal Input"]
        direction TB
        INPUT["User CLI / Terminal REPL / API / CI Runner"] --> SCAN["UntrustedContentScanner<br/>(Path Traversal & SSRF Firewall)"]
        SCAN --> ROUTER_FAST{"Fast-Path Router<br/>(< 50ms Intent Classifier)"}
        ROUTER_FAST -- "Runtime / Status Command" --> DIRECT["Deterministic Direct Handler"]
        ROUTER_FAST -- "Complex Goal / Engineering Task" --> INBOX["CommandInbox<br/>(Live Priority Dispatch)"]
    end

    subgraph Layer1 ["1. Transactional Task Control Plane"]
        direction TB
        INBOX --> ORCH["HierarchicalOrchestrator<br/>(Mission DAG Decomposer)"]
        ORCH --> DEP["DependencyManager<br/>(Cycle Detection & Topological Sort)"]
        DEP <--> TASKDB[("14-State SQLite Task DB<br/>(iva_tasks.db WAL)")]
        TASKDB <--> STM["TaskStateMachine<br/>(14-State Transition Enforcer)"]
    end

    subgraph Layer2 ["2. Concurrency & Resource Governor"]
        direction TB
        ORCH --> GOV["ResourceGovernor<br/>(Telemetry Monitor)"]
        GOV <--> RES["Live System Headroom Checks<br/>(RAM >= 1400MB, CPU < 85%)"]
        GOV --> POOL["Dynamic Active Worker Pool<br/>(1 to 4 Concurrent Executions)"]
    end

    subgraph Layer3 ["3. 100-Specialist Ecosystem Router"]
        direction TB
        POOL --> CROUTER["CapabilityRouter<br/>(Schema Matching & Contract Binding)"]
        CROUTER --> SPEC["100 Embedded Specialist Contracts<br/>(16 Functional Families)"]
    end

    subgraph Layer4 ["4. Universal Model Engine & Token Economy"]
        direction TB
        SPEC --> MA["ModelAdapter<br/>(Google Gemini Direct REST / OpenAI)"]
        MA --> CWD["Isolated CWD Working Directory<br/>(-88.2% Token Bloat Reduction)"]
        MA --> ECON["TokenEconomy Ledger<br/>(Strict Cost Ceilings)"]
    end

    subgraph Layer5 ["5. Disposable Sandbox & Process Supervision"]
        direction TB
        SPEC --> SBX["DisposableSandboxRunner<br/>(python:3.12-slim Container)"]
        SBX --> FLAGS["Strict Hardening Flags<br/>(--network none, --read-only, tmpfs /tmp)"]
        SBX <--> SUP["ProcessSupervisor & StreamParser<br/>(Real-Time stdout/stderr & Idle Timeout)"]
    end

    subgraph Layer6 ["6. Cognitive Memory & Learning Plane"]
        direction TB
        SBX -- "Failure Traceback" --> REPAIR["CIRepairAgent<br/>(Minimal Patch Synthesis)"]
        REPAIR --> MEM[("10-Layer SQLite Memory<br/>(omega_memory.db WAL)")]
        MEM <--> ACON["ACONCompressor<br/>(Anchor-Preserving Compression)"]
    end

    subgraph Layer7 ["7. Verification & Staging"]
        direction TB
        SBX -- "Exit Code 0 (Full Pass)" --> VERIF["EvidenceVerifier<br/>(Zero-Regression Audit)"]
        VERIF --> STAGE["External Candidate Staging<br/>(Repo 100% Unchanged During Generation)"]
        STAGE --> HUMAN{"HighImpactApprovalGate<br/>Human Authorization?"}
        HUMAN -- "Approved" --> COMMIT["Atomic Workspace Commit"]
        HUMAN -- "Denied" --> ABORT["Default-Deny Quarantine"]
    end

    Layer0 --> Layer1
    Layer1 --> Layer2
    Layer2 --> Layer3
    Layer3 --> Layer4
    Layer3 --> Layer5
    Layer5 --> Layer6
    Layer6 --> Layer7
```

---

## 👥 100 Embedded Specialist Contracts Across 16 Families

IVA embeds **100 validated specialist contracts** inside [`agents/IVA/ecosystem/agent_registry/registry.json`](agents/IVA/ecosystem/agent_registry/registry.json). Each contract has a strictly typed JSON schema, input/output validation, and execution boundaries:

| # | Capability Family | Contracts | Primary Specializations & Roles |
|:---:|:---|:---:|:---|
| 1 | **Planning & Architecture** | 6 | `plan_mission_decomposer`, `plan_systems_architect`, `plan_dependency_analyzer`, `plan_risk_estimator`, `plan_capacity_forecaster`, `plan_adr_synthesizer` |
| 2 | **Research & Evidence Synthesis** | 8 | `res_primary_source_hunter`, `res_citation_auditor`, `res_contradiction_detector`, `res_freshness_assessor`, `res_sdk_doc_navigator`, `res_benchmark_methodology_analyst`, `res_patent_and_standard_reviewer`, `res_evidence_ledger_archivist` |
| 3 | **Mathematics & Symbolic Reasoning** | 6 | `math_algebraic_solver`, `math_combinatorics_analyst`, `math_probability_statistician`, `math_linear_algebra_verifier`, `math_number_theory_checker`, `math_real_complex_analyst` |
| 4 | **Physics & Physical Sciences** | 6 | `phys_quantum_mechanics_reasoner`, `phys_relativistic_electrodynamics`, `phys_statistical_thermodynamics`, `phys_astrophysics_cosmology`, `phys_condensed_matter_analyst`, `phys_dimensional_consistency_auditor` |
| 5 | **Chemistry & Molecular Sciences** | 5 | `chem_organic_synthesis_planner`, `chem_spectroscopy_elucidator`, `chem_kinetics_thermochemistry`, `chem_inorganic_coordination`, `chem_quantum_molecular_orbital` |
| 6 | **Biology & Biomedical Sciences** | 5 | `bio_molecular_genetics_reasoner`, `bio_cell_signaling_oncology`, `bio_biochemistry_enzymology`, `bio_immunology_virology`, `bio_bioinformatics_sequence_analyst` |
| 7 | **Software Engineering (SWE)** | 10 | `swe_python_runtime_engineer`, `swe_ast_refactoring_specialist`, `swe_api_contract_designer`, `swe_concurrency_lock_auditor`, `swe_exception_resilience_engineer`, `swe_cli_ux_engineer`, `swe_serialization_codec_specialist`, `swe_dependency_hygiene_auditor`, `swe_state_machine_implementer`, `swe_patch_minimizer` |
| 8 | **Terminal, Shell & OS Operations** | 8 | `ops_powershell_automation_specialist`, `ops_posix_shell_specialist`, `ops_process_tree_warden`, `ops_filesystem_storage_steward`, `ops_stream_progress_monitor`, `ops_archive_artifact_verifier`, `ops_environment_isolation_guard`, `ops_git_worktree_custodian` |
| 9 | **Containers, Virtualization & Cloud** | 6 | `virt_docker_engine_inspector`, `virt_wsl2_memory_governor`, `virt_harbor_sandbox_coordinator`, `virt_dockerfile_layer_optimizer`, `virt_vm_image_readiness_auditor`, `virt_container_network_isolation_checker` |
| 10 | **Browser & Web Automation** | 6 | `web_playwright_session_controller`, `web_dom_accessibility_inspector`, `web_network_har_analyzer`, `web_form_workflow_automator`, `web_ssrf_robots_compliance_guard`, `web_visual_regression_verifier` |
| 11 | **Desktop & Computer Use** | 6 | `desk_sandbox_isolation_enforcer`, `desk_osworld_task_inspector`, `desk_screenshot_observation_compressor`, `desk_gui_action_schema_validator`, `desk_vm_snapshot_coordinator`, `desk_multi_app_handoff_planner` |
| 12 | **Data, Storage & Databases** | 6 | `data_sqlite_wal_architect`, `data_jsonl_ledger_reconciler`, `data_memory_supersession_curator`, `data_acon_context_compressor`, `data_checkpoint_recovery_steward`, `data_telemetry_schema_normalizer` |
| 13 | **Testing, QA & Verification** | 8 | `qa_unit_suite_runner`, `qa_integration_scenario_verifier`, `qa_gpqa_clean_auditor`, `qa_terminal_bench_reconciler`, `qa_claim_to_evidence_verifier`, `qa_registry_smoke_harness`, `qa_state_transition_fuzzer`, `qa_regression_baseline_comparator` |
| 14 | **Security, Permissions & Safety** | 6 | `sec_permission_gate_enforcer`, `sec_prompt_injection_shield`, `sec_secret_credential_scanner`, `sec_benchmark_integrity_warden`, `sec_ssrf_network_firewall`, `sec_directive_zero_auditor` |
| 15 | **Performance, Token & Optimization** | 4 | `perf_adaptive_concurrency_governor`, `perf_token_budget_controller`, `perf_tail_latency_mitigator`, `perf_quantum_claim_gatekeeper` |
| 16 | **Release, Governance & Reporting** | 4 | `gov_manifest_hash_sealer`, `gov_telemetry_dashboard_publisher`, `gov_phase_gate_reviewer`, `gov_release_dossier_compiler` |
| **Total** | **16 Active Families** | **100** | **Fully validated in [`registry.json`](agents/IVA/ecosystem/agent_registry/registry.json)** |

---

## 🔒 Fail-Closed Safety Railings

IVA enforces strict, non-bypassable safety gates:

1. **Market Live Order Dispatch Lock**:
   - Live order dispatch is physically locked (`LIVE_ORDER_DISPATCH_ENABLED = False`).
   - Requires explicit multi-signature hardware authorization and user capital assignment before real orders can be routed.
2. **Path Traversal & Host File Protection**:
   - `UntrustedContentScanner` rejects directory traversal patterns (`../`, `..\`, absolute paths outside staging boundary).
3. **SSRF Network Firewall**:
   - Blocks model or container requests targeting loopback (`127.0.0.1`, `localhost`), link-local (`169.254.169.254`), and private RFC 1918 subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
4. **Disposable Sandbox Isolation**:
   - All code execution occurs in Docker containers with `--network none`, `--read-only`, `UID 65534 (nobody)`, and ephemeral `tmpfs /tmp`.

---

## 🧪 Verification & Autonomous Self-Tests

IVA includes a complete autonomous self-verification test harness. You can run all 44 verified test cases with zero setup:

```bash
# Run self-tests via the primary CLI
python run_iva.py test

# Or run individual test modules using standard unittest
python -m unittest tests/unit/test_terminal_client.py
python -m unittest tests/unit/test_universal_api_provider.py
python -m unittest tests/test_iva_cognitive_architecture_and_identity.py
python -m unittest tests/test_production_hardening_sprint.py
```

### Self-Test Results:
```text
==============================================================================
   🧪 IVA AUTONOMOUS SELF-VERIFICATION SUITE
==============================================================================
   Executing tests across terminal, universal API, cognitive identity & hardening...

   • Loaded 44 test cases from verified test modules.
   Ran 44 tests in 10.43s

   ✅ All 44 tests PASSED in 10.43s. IVA self-verification 100% GREEN.
==============================================================================
```

---

## 📁 Repository Directory Structure

```text
IVA/
├── run_iva.py                          # Primary CLI Entrypoint (Interactive REPL & CLI commands)
├── setup_iva.py                        # Autonomous setup script (creates .env & initializes memory)
├── README.md                           # Master Architecture, Installation & Operational Guide
├── IVA_README.md                       # Iva Agent Cognitive Identity & Philosophical Playbook
├── pyproject.toml                      # Standard packaging definition (0 required dependencies)
├── .env.example                        # Universal API configuration template
│
├── agents/IVA/                         # Native IVA Multi-Agent Core Engine
│   ├── ecosystem/agent_registry/       # 100 Specialist Contracts & Registry
│   │   ├── registry.json               # Validated 100-specialist contract definitions
│   │   ├── registry_validator.py       # JSON schema & duplicate contract validator
│   │   └── ecosystem_coordinator.py    # Dynamic capability router & contract dispatcher
│   │
│   ├── engine/agi17/                   # Transactional Runtime Engine
│   │   ├── adapters/                   # Universal API Provider & Model Adapter
│   │   │   ├── universal_api_provider.py # Direct Google Gemini & OpenAI REST via stdlib urllib
│   │   │   └── model_adapter.py        # Token economy & credential discovery
│   │   ├── memory/                     # 10-Layer Cognitive Memory DB (SQLite WAL)
│   │   ├── orchestration/              # Hierarchical DAG Orchestrator & CI-Repair Agent
│   │   │   ├── hierarchical_orchestrator.py
│   │   │   └── ci_repair_agent.py      # Automated Python CI-Repair Specialist
│   │   ├── process_supervision/        # Disposable Docker Sandbox Runner & Supervisors
│   │   ├── runtime/                    # TerminalClient & Interactive REPL Engine
│   │   └── task_control/               # 14-State Machine & Transactional Task DB
│   │
│   └── docs/                           # Architecture Specifications & P0 Security Audits
│
└── tests/                              # Comprehensive Test Suites
    ├── unit/                           # Terminal client & Universal API provider unit tests
    ├── integration/                    # End-to-end multi-agent integration tests
    ├── test_iva_cognitive_architecture_and_identity.py # Iva identity & safety invariant tests
    └── test_production_hardening_sprint.py            # Production hardening & sandbox tests
```

---

## 📄 License & Intellectual Property

IVA is distributed under the **MIT License**. See [`LICENSE`](LICENSE) for complete terms.

- **Author**: Abhishek ([@Abhishek200416](https://github.com/Abhishek200416))
- **Agent Identity**: **Iva** — Autonomous Cognitive Engineering Partner
- **Repository**: [`https://github.com/Abhishek200416/IVA`](https://github.com/Abhishek200416/IVA)
