# intentprobe — Roadmap & Project State

> Single source of truth for where this project is. Update after each milestone so any new session can resume from this file alone.

## What this is

An activation-probe security scanner for AI agent tooling. Before an agent installs an MCP server, a Claude Code skill, or an npm package, intentprobe reads a small local model's internal activations to detect tool poisoning that text and regex scanners miss. It ships as a pre-install hook, so the agent runs it automatically before adding any tool.

It is the first scanner to use model internals instead of regex / AST / LLM-as-judge. Apache-2.0, research preview.

Backed by research: a 60-rule regex scanner catches **0 / 485** on the MCPTox benchmark, while an activation probe scores **97%** on matched pairs where the safe and poisoned descriptions share the same vocabulary.

## Roadmap

- [x] **1. Name + repo.** `intentprobe` (npm unscoped + `@mcpware` both free; survived competitive / SEO / trademark research against trueye, klyro, probescan, latens, etc). Repo scaffolded, Apache-2.0.
- [~] **2. Spike: validate a modern sub-2B model's probe.** Qwen2.5-0.5B activations on the hard_v3 (100+100) and neutral (15+15) sets vs a TF-IDF baseline. Goal: confirm the pipeline works and a modern small model matches or beats the GPT-2 reference (paper: GPT-2 probe 98.5% on hard_v3 where TF-IDF is 79.5%).
- [ ] **3. Pick final base model + train production probe.** Must be sub-2B so it runs on any CPU (Gemma 4 E2B vs Qwen2.5-1.5B; Gemma is gated and needs an HF token). Re-train the probe on the chosen model — a GPT-2 probe does NOT transfer (different activation dimension and coordinate space). Export the probe weights.
- [ ] **4. intentprobe Python CLI.** `intentprobe scan <target>`: load base model -> extract activations -> apply probe -> safe / suspicious / poisoned + confidence. Full error handling + debug logging. QA tests.
- [ ] **5. Pre-install hook.** Claude Code PreToolUse hook + npm preinstall hook. Install once, transparent after. E2E QA: a known poisoned tool is actually blocked.
- [ ] **6. Research-preview README + crowdsource + publish.** Honest about the ~71-73% cross-phrasing frontier; collect real poisoned samples from users (feeds the underlying research). npm publish + GitHub push (org: mcpware, tentative).

## Key technical facts (do not relearn these)

- The probe consumes **activations, not text**. Every scan runs the base model's forward pass (stop at a middle layer, no generation, no GPU; a sub-2B model on CPU is roughly sub-second per description).
- The probe weights are tiny (a few KB) but **cannot run standalone** — they need the base model to turn text into activations. So the base model must be small enough to run on any user machine (sub-2B). A large model excludes users with no GPU.
- Training and runtime are both **Python** (torch + transformers + sklearn). A hook just spawns the command, so users never see the runtime — `npx` vs `pipx` does not matter to them.
- **Research-preview positioning**: lead with the cases where text scanners hit 0 and the probe hits 97. Cross-phrasing generalization (~71-73%) is the open frontier — stay honest, and crowdsource real samples.
- The probe **detects and flags for a human**. It never tries to silently "fix" a tool from the inside.

## Where things live

- Training / eval data: the MCPTox + matched-pair / hard / neutral benchmark sets from the activation-probe research (not yet vendored into this repo).
- Spike / exploration code: kept outside the repo during R&D; the cleaned-up training script will land in `training/`.
- Research paper: "Can Model Internals Detect MCP Tool Poisoning That Text Analysis Cannot?"

## Current status

Step 2 in progress. Spike v2 running (Qwen2.5-0.5B on hard_v3 + neutral). Awaiting numbers to decide step 3 (final base model). This section gets updated the moment the spike returns.
