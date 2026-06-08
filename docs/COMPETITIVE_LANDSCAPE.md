# Competitive Landscape

Last checked: 2026-06-08.

IntentProbe is not another prompt-injection keyword list. It is a local
activation-probe scanner for MCP servers, skills, packages, and runtime tool
events: it runs a small frozen model locally, reads internal activations, and
classifies the model state.

That puts it in a different bucket from the current market.

## One-Screen Map

| Category | Examples checked | Usual method | Main limitation | IntentProbe difference |
|---|---|---|---|---|
| Enterprise cloud/API guardrails | Lakera Guard, Azure Prompt Shields, Google Model Armor, AWS Bedrock Guardrails, Pangea/CrowdStrike AI Guard, OpenAI Guardrails, Cisco AI Defense, HiddenLayer | Send prompts, documents, tool calls, or responses to a vendor/cloud guardrail | Detector internals and benchmark harnesses are usually not reproducible by the user; SaaS/API modes require sending content to a provider | Local by default; benchmark scripts and scanner artifact are in this repo |
| Agent/MCP scanners and firewalls | Snyk Agent Scan, former Invariant MCP-Scan, MCP Scanner, MEDUSA, Sunglasses, Armorer Guard, ClawGuard, SkillsSafe, AgentSeal, mcpwn, MCPRadar | Static rules, signatures, policy checks, proxies, metadata scanning, optional cloud/API verification | Strong hygiene layer, but public material is rule/pattern/policy/API oriented rather than activation-probe based | Uses a model-internal activation signal for tool intent, plus static corroboration |
| Text classifiers | ProtectAI/LLM Guard DeBERTa, Meta Prompt Guard / Llama Prompt Guard 2 | Classify text as benign, prompt injection, or jailbreak | Learns surface/task patterns; can miss same-vocabulary tool poisoning where the bad intent is a subtle capability expansion | Reads hidden states after the local model has represented the tool description |
| LLM-as-judge guardrails | NeMo self-check rails, OpenAI Guardrails prompt-injection check, Promptfoo graders, custom judge prompts | Ask another LLM whether an action/input/output is unsafe | Token cost, latency, model/version drift, and prompt fragility | Small local scanner, deterministic score for a fixed artifact |
| Red-team frameworks | garak, Giskard, Promptfoo red team | Generate attacks and grade whether an LLM/app fails | Great for audits, but not the same job as a pre-install scanner or cheap runtime hook | CLI scans before install and can sit at runtime tool boundaries |

## Short Positioning

Enterprise guardrails ask a vendor backend. Text classifiers read surface
patterns. LLM judges ask another model for an opinion. Local rule scanners match
known suspicious patterns.

IntentProbe reads the local model's internal state after it has processed the
tool description.

The public claim we can defend:

> IntentProbe is the first product-shaped MCP/tool-poisoning scanner we know of
> that uses an activation probe as the main signal instead of only regex,
> static rules, text classifiers, cloud guardrail APIs, or LLM-as-judge checks.

## Direct MCP / Agent Scanner Competitors

### Snyk Agent Scan

Snyk Agent Scan is the closest public product-shaped competitor. Its README says
it discovers and scans agent components, MCP servers, and skills for prompt
injections and vulnerabilities. It supports Claude, Cursor, Windsurf, Gemini
CLI, VS Code, Claude Code, and other agent surfaces.

Important public details:

- It can execute stdio MCP server commands to retrieve tool descriptions, with
  interactive consent by default.
- It validates components with local checks and by invoking the Agent Scan API.
- Its README states that skills, agent applications, tool names, and
  descriptions are shared with Snyk for analysis.
- Its background mode reports results to a Snyk Evo instance for enterprise
  monitoring.

Source: <https://github.com/snyk/agent-scan>

Our comparison:

- Snyk is a real agent scanner, not a toy baseline.
- Its public client exposes a scan-and-upload/API validation shape; the remote
  detector is opaque from the user's machine.
- It does not publicly expose an activation-probe method.
- Its public repo does not provide a user-reproducible benchmark proving
  tool-poisoning accuracy on our matched-intent cases.

Our reproducible local head-to-head is against the ProtectAI DeBERTa
prompt-injection classifier that we used as the source-verified
Snyk/Invariant-style text-classifier baseline:

| Test | IntentProbe / activation probe | DeBERTa text-classifier baseline |
|---|---:|---:|
| Same-words different-intent set (`n=86`) | 97.7% recall, 96.6% F1 | 0.0% recall, 0.0% F1 |
| MCPTox held-out split (`n=249`) | 100.0% recall, 99.3% F1 | 19.9% recall, 33.0% F1 |

Repro artifact:
`research/benchmark-results-deberta-vs-probe-2026-05-31.md`.

The fair framing is not "DeBERTa is bad." The fair framing is: a
prompt-injection text classifier is out-of-distribution on subtle tool
poisoning, while activation probes show a separate signal.

### Former Invariant MCP-Scan

Invariant MCP-Scan was an MCP-focused scanner with static scan and proxy modes.
The public Invariant docs describe scanning Claude, Cursor, Windsurf, and other
MCP client configurations; checking tool descriptions for prompt injection and
tool poisoning; monitoring MCP traffic; enforcing tool restrictions; detecting
tool shadowing; and pinning tools to detect rug pulls.

Sources:

- <https://invariantlabs-ai.github.io/docs/mcp-scan/>
- <https://explorer.invariantlabs.ai/docs/mcp-scan/>
- <https://github.com/invariantlabs-ai/explorer>

Our comparison:

- Strong MCP product shape.
- Strong operational scanner/proxy concept.
- Public docs describe rules, guardrails, hashing, proxying, and external
  verification, not activation-probe internals.
- The Invariant GitHub route now redirects toward Snyk Agent Scan; hosted
  Explorer material points users toward Snyk AI Security.

### New Local MCP / Agent Scanners

This space is filling quickly. The most relevant current public scanners we
found are listed below.

| Product/project | Public positioning | Method shape from public material | How IntentProbe differs |
|---|---|---|---|
| MCP Scanner | Open-source MCP scanner for tool poisoning, prompt injection, rug pulls, and cross-origin escalation | Rule categories and MCP security checks | IntentProbe adds activation features for subtle same-word intent shifts |
| MEDUSA | AI security scanner with 9,600+ detection rules for prompt injection, MCP tool poisoning, RAG poisoning, and agent attacks | Large rule/pattern catalog and SAST-style scanner | IntentProbe is narrower but model-internal rather than rule-count driven |
| Sunglasses | Local open-source AI-agent scanner/filter for prompt injection, tool poisoning, malicious READMEs, credential exfiltration | Pattern catalog, keywords, normalization, local filter | IntentProbe's differentiator is activation state, not text pattern coverage |
| Armorer Guard | Local Rust scanner for prompts, outputs, tool arguments, MCP proxying, credentials, exfiltration, dangerous tool calls | Fast local structured rule/scoring boundary scanner | IntentProbe is slower but uses a learned activation probe for tool intent |
| ClawGuard | Security scanning for AI agent skills; CLI/registry/hooks; detects prompt injections, secrets, malware, permissions | Scanner plus hooks/proxy/security registry shape | IntentProbe focuses the core signal on activation-probed intent |
| SkillsSafe | AI skill scanner for SKILL.md, MCP configs, system prompts, credential theft, exfiltration, hidden instruction patterns | Skill/MCP pattern scanning before install | Same install-time moment, different signal class |
| AgentSeal | Open-source security scanner for AI agents and MCP/tool poisoning | Red-team/scanner positioning for agent security | Public material does not show activation-probe scanning |
| mcpwn / MCPRadar / MEOK-style scanners | MCP security scanners for prompt injection, tool poisoning, path traversal, command execution, SSRF, and related risks | MCP-specific rules, probes, and protocol/security checks | Good complementary hygiene; not the same as activation probing |

Representative sources:

- <https://mcpscanner.cloud/>
- <https://pantheonsecurity.io/>
- <https://sunglasses.dev/open-source-ai-agent-security-scanner>
- <https://armorerlabs.com/blog/armorer-guard-inline-prompt-injection-defense>
- <https://www.clawguard.sh/>
- <https://skillssafe.com/en>
- <https://agentseal.org/>
- <https://safematix.com/mcpwn/>
- <https://mcpradar.dev/>
- <https://mcpservers.org/es/servers/csoai-org/meok-mcp-injection-scan-mcp>

Our comparison:

- These products make the category more real. That helps IntentProbe, because it
  proves scan-before-install and runtime tool-boundary scanning are becoming
  normal expectations.
- Most public descriptions emphasize pattern/rule coverage, latency, MCP proxy
  placement, credential redaction, and known attack categories.
- We did not find another installable local MCP/tool scanner whose primary
  signal is a model activation probe.

## Enterprise Cloud / API Guardrails

These products are serious enterprise controls. The issue is not that they are
useless. The issue is that a developer often cannot independently verify the
detector internals or reproduce the advertised accuracy on a local MCP/tool
poisoning benchmark. SaaS/API modes also mean prompts, tool data, or outputs are
sent to a provider.

### Lakera Guard

Lakera Guard documents real-time visibility, threat detection, prompt-attack
detection, data-leakage controls, centralized policy management, and
SaaS/self-hosted deployment options. Its integration docs describe calling the
Lakera Guard API for user interactions or agent steps.

Sources:

- <https://docs.lakera.ai/guard>
- <https://docs.lakera.ai/docs/api/guard>

Comparison:

- Good enterprise control plane.
- Public docs claim high-accuracy threat detection, but the detector and
  benchmark harness are not reproducible by the user from the docs.
- SaaS mode means prompts/reference materials are sent to Lakera's API.
- IntentProbe runs locally and exposes its benchmark scripts.

### Microsoft Azure Prompt Shields

Azure Prompt Shields targets user prompt attacks and document/indirect prompt
injection. The docs list attack classes such as changing system rules,
conversation mockups, role-play, and encoding attacks.

Source:
<https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/content-filter-prompt-shields>

Comparison:

- Strong cloud-platform integration.
- Cloud service; detector internals and benchmark set are not exposed as a
  reproducible scanner artifact.
- It is built for prompt/document filtering around Azure AI workloads, not
  specifically as a local scan-before-install MCP/skill scanner.

### Google Cloud Model Armor

Model Armor screens prompts and responses, supports prompt injection/jailbreak
detection, sensitive data protection, malicious URL detection, and confidence
thresholds.

Source: <https://docs.cloud.google.com/model-armor/overview>

Comparison:

- Useful cloud AI security layer.
- It is a Google Cloud service, not a local open scanner.
- Public docs describe configuration and thresholds, not a reproducible
  benchmark on MCP/tool poisoning.

### Amazon Bedrock Guardrails

Bedrock Guardrails supports prompt attack filters through the console or API.
AWS requires tagging user input for prompt-attack filtering in InvokeModel and
InvokeModelWithResponseStream use cases; without tags, the filter does not apply
for those cases.

Source:
<https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-prompt-attack.html>

Comparison:

- Strong inside Bedrock workflows.
- Cloud/API integration rather than local scanner.
- Depends on app-side tagging and guardrail configuration.
- Public docs do not provide a reproducible MCP/tool-poisoning benchmark.

### Pangea / CrowdStrike AI Guard and Prompt Guard

Pangea's docs describe AI Guard and Prompt Guard as API/SDK services for
detecting direct and indirect prompt injection, malicious content, PII, and
other AI traffic risks.

Sources:

- <https://pangea.cloud/docs/ai-guard>
- <https://pangea.cloud/docs/prompt-guard/>

Comparison:

- Enterprise API guardrail.
- The detection backend and benchmark details are vendor-side.
- Useful for production app traffic; not a local activation-probe scanner for
  install-time MCP/tool descriptions.

### Cisco AI Defense and HiddenLayer

Cisco AI Defense documents runtime protection and an Inspection API for prompt
injection, denial-of-service, and data leakage. HiddenLayer documents AI runtime
security for prompt attacks, jailbreaks, unsafe outputs, and malicious tool use.

Sources:

- <https://developer.cisco.com/docs/ai-defense-inspection/>
- <https://docs.hiddenlayer.ai/docs/products/aidr-g/overview>
- <https://www.hiddenlayer.com/platform/ai-runtime-security>

Comparison:

- Serious enterprise AI security stacks.
- Public product docs do not disclose enough detector/benchmark detail for a
  user to reproduce MCP/tool-poisoning accuracy.
- IntentProbe is narrower, but local and inspectable.

## Text Classifier Competitors

### ProtectAI / LLM Guard DeBERTa

LLM Guard's prompt-injection scanner uses a fine-tuned DeBERTa classifier. Its
docs describe a binary prompt-injection classification model: `0` for no
injection and `1` for injection detected. The docs also say the scanner is not
recommended for system prompts.

Sources:

- <https://github.com/protectai/llm-guard/blob/main/docs/input_scanners/prompt_injection.md>
- <https://huggingface.co/protectai/deberta-v3-base-prompt-injection-v2>

Comparison:

- This is a real local text classifier.
- It detects classic prompt-injection strings correctly in our sanity check.
- It misses subtle same-vocabulary tool poisoning in our benchmark.
- This is exactly the difference between "text resembles prompt injection" and
  "tool description encodes unsafe intent."

### Meta Prompt Guard

Meta's Prompt Guard and Llama Prompt Guard 2 are text-classification models for
benign / injection / jailbreak categories. The Llama Prompt Guard 2 docs
describe a fine-tuned BERT/DeBERTa-style classifier for direct jailbreak and
prompt-injection-style attacks.

Sources:

- <https://huggingface.co/meta-llama/Prompt-Guard-86M>
- <https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M>
- <https://meta-llama.github.io/PurpleLlama/LlamaFirewall/docs/documentation/scanners/prompt-guard-2>

Comparison:

- Small and local-friendly.
- Useful as a prompt/jailbreak classifier.
- Still a text classifier; public model cards do not make it an MCP
  tool-intent activation scanner.

## LLM-as-Judge and Red-Team Frameworks

### NVIDIA NeMo Guardrails self-checking

NeMo Guardrails documents `self_check_input`, where the LLM is prompted to
answer whether the user input should be allowed. NVIDIA explicitly notes that
performance depends strongly on the capability of the LLM to follow the
self-check prompt.

Source:
<https://docs.nvidia.com/nemo/guardrails/latest/configure-rails/guardrail-catalog/self-check.html>

Comparison:

- Flexible and easy to understand.
- It asks another LLM to judge the prompt.
- That costs tokens, adds latency, and can vary with model/version/prompt.
- IntentProbe's probe score is deterministic for a fixed artifact.

### OpenAI Guardrails prompt-injection check

OpenAI Guardrails documents a prompt-injection detection check that uses
LLM-based analysis on function calls and tool-call outputs, with a configurable
model, confidence threshold, and token usage in the returned result.

Source:
<https://openai.github.io/openai-guardrails-js/ref/checks/prompt_injection_detection/>

Comparison:

- Strong agent-flow alignment check.
- It is explicitly LLM-based analysis, not a local activation scanner.
- It is better compared to runtime judge guardrails than to install-time MCP
  scanner artifacts.

### Promptfoo red-team graders

Promptfoo is a strong eval/red-team framework. Its docs describe red-team
attack generation and grading; graders can be LLM-based and configurable.

Sources:

- <https://www.promptfoo.dev/docs/red-team/configuration/>
- <https://www.promptfoo.dev/docs/red-team/troubleshooting/grading-results/>

Comparison:

- Excellent for testing an app or agent.
- Not the same job as a local scanner that runs before installing a tool.
- LLM-based grading is useful for audits but not ideal as a cheap deterministic
  runtime hook.

### garak and Giskard

garak is an LLM vulnerability scanner with prompt-injection probes. Giskard
provides LLM vulnerability scanning and detectors for injection-style failures.

Sources:

- <https://docs.garak.ai/garak/examples/prompt-injection>
- <https://docs.giskard.ai/hub/sdk/scan/index.html>
- <https://docs.giskard.ai/en/latest/reference/scan/llm_detectors.html>

Comparison:

- Useful for red-team campaigns and vulnerability assessment.
- They test whether a target LLM/app can be made to fail.
- IntentProbe is aimed at a different moment: before trusting a tool, skill, MCP
  server, package, or runtime tool event.

## What We Can Say Publicly

Strong version:

> IntentProbe is the first product-shaped activation-probe scanner we know of
> for MCP/tool poisoning. It runs locally, reads model activations, and ships
> with reproducible benchmark artifacts.

Why this is defensible:

- We found public MCP/agent scanners, cloud guardrails, prompt-injection text
  classifiers, LLM-as-judge guardrails, and red-team frameworks.
- We did not find another installable local MCP/tool scanner whose main signal
  is a model-internal activation probe.
- IntentProbe publishes the scanner artifact, methodology files, benchmark
  scripts, and comparison reports in this repo.

What not to overclaim:

- Do not say cloud guardrails are useless. They are useful enterprise controls.
- Do not say text classifiers are bad. They solve a different task and can catch
  classic prompt injection.
- Do not say local rule scanners are pointless. They are fast and useful for
  known patterns.
- Do not say IntentProbe catches everything. External generalization is still
  the frontier.
- Do not say every benchmark is apples-to-apples. Our DeBERTa comparison is
  intentionally showing out-of-distribution failure on tool poisoning.

## Clean Public Soundbite

Most scanners ask: "Does this text look suspicious?"

IntentProbe asks: "When a small model reads this tool, does its internal state
look like it understood a malicious capability?"
