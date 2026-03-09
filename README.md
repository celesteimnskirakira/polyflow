# Polyflow

[![PyPI version](https://img.shields.io/pypi/v/polyflow-ai.svg)](https://pypi.org/project/polyflow-ai/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-64%20passing-brightgreen.svg)](#)

**Three models check the same thing. Consensus beats any single AI.**

Run Claude, Gemini, and GPT-4 in parallel on the same task — they cross-validate each other, vote on findings, and synthesize a final answer. No single model's blind spots. No boilerplate. One YAML file.

```bash
pip install polyflow-ai
export OPENROUTER_API_KEY=sk-or-...
polyflow run code-review-multi-model -i "$(git diff HEAD~1)"
```

Or as a GitHub Action on every PR — fully automated, no human in the loop required:

```yaml
- uses: celesteimnskirakira/polyflow@main
  with:
    workflow: code-review-multi-model
    input: ${{ steps.diff.outputs.content }}
    openrouter-api-key: ${{ secrets.OPENROUTER_API_KEY }}
```

---

## Why three models?

No AI model is right 100% of the time. But when Claude, Gemini, and GPT-4 **all agree**, that's a signal worth trusting. When they disagree, that's where the interesting problems are.

```
Single model:  Claude says "no security issues"   → might have blind spots

Three models:  Claude says "no security issues"
               Gemini finds SQL injection          → consensus surfaces the real finding
               GPT-4 finds missing auth check
               Claude synthesizes final report
```

This isn't about needing humans to be smarter than AI. It's about **models checking each other** — the same principle behind code review, peer review, and ensemble methods in ML.

---

## Install

```bash
pip install polyflow-ai
```

Requires Python 3.11+.

**One key covers all three models** (recommended):

```bash
export OPENROUTER_API_KEY=sk-or-...    # openrouter.ai — Claude + Gemini + GPT-4
```

Or configure per-model:

```bash
polyflow init     # interactive setup
polyflow doctor   # verify everything works
```

---

## Quick Start

```bash
# Browse 22 ready-to-use workflows
polyflow list

# Code review: Claude + Gemini + GPT-4 in parallel
polyflow run code-review-multi-model -i "$(git diff HEAD~1)"

# Security audit with consensus findings
polyflow run security-audit -i "$(cat src/auth.py)"

# Bug triage across models
polyflow run bug-triage -i "TypeError: 'NoneType' object is not subscriptable in auth.py:42"

# Generate a custom workflow
polyflow new "three models review my API design, synthesize best approach" -o api-review.yaml
```

---

## How It Works

The core primitive is a **parallel step with aggregation** — send the same prompt to multiple models, collect results, synthesize:

```yaml
name: security-consensus
description: "Three models find vulnerabilities. Consensus = high confidence."

steps:
  - id: audit
    type: parallel
    steps:
      - id: claude
        model: claude
        prompt: "Find security vulnerabilities (OWASP Top 10): {{input}}"
      - id: gemini
        model: gemini
        prompt: "Find security vulnerabilities (OWASP Top 10): {{input}}"
      - id: gpt4
        model: gpt-4
        prompt: "Find security vulnerabilities (OWASP Top 10): {{input}}"
    aggregate:
      mode: vote            # findings all three agree on = high confidence
      model: claude         # Claude writes the final synthesized report
      prompt: |
        Three models independently audited this code.
        Synthesize their findings. Mark consensus findings as HIGH CONFIDENCE.
        Disagreements as NEEDS REVIEW.
        {{aggregated}}

output:
  format: markdown
  save_to: security-report.md
```

Run it anywhere — terminal, CI/CD, GitHub Actions — with no human approval needed:

```bash
polyflow run security-consensus --ci -i "$(cat src/auth.py)"
```

---

## Core Concepts

### Parallel Steps + Aggregation

The engine that makes multi-model consensus work:

```yaml
- id: cross_validate
  type: parallel
  steps:
    - id: model_a
      model: claude
      prompt: "..."
    - id: model_b
      model: gemini
      prompt: "..."
    - id: model_c
      model: gpt-4
      prompt: "..."
  aggregate:
    mode: vote        # vote | diff | summary | raw
    model: claude     # synthesis model (optional)
    prompt: "Synthesize: {{aggregated}}"
```

| Aggregate mode | When to use |
|---|---|
| `vote` | Find what all models agree on — highest confidence findings |
| `diff` | Show where models disagree — useful for exploring trade-offs |
| `summary` | Let a fourth model synthesize all outputs into one report |
| `raw` | Return all outputs separately for manual inspection |

### Template Expressions

| Expression | Description |
|---|---|
| `{{input}}` | Input passed with `-i` |
| `{{steps.step_id.output}}` | Output from a previous step |
| `{{aggregated}}` | Combined output inside an `aggregate.prompt` |
| `{{vars.key}}` | Workflow variable |
| `{{context}}` | Injected file/directory context |
| `{{a \| b}}` | Fallback: use `b` if `a` is empty |

### Sequential + Conditional Pipelines

Chain parallel consensus results into further steps:

```yaml
steps:
  - id: find_issues
    type: parallel          # three models find issues
    steps: [...]
    aggregate:
      mode: vote
      model: claude

  - id: generate_fix        # Claude writes the fix based on consensus
    model: claude
    prompt: |
      Consensus issues found:
      {{steps.find_issues.output}}

      Write a fix for each HIGH CONFIDENCE issue.
      Input code: {{input}}
```

### Human-in-the-Loop (optional)

For decisions that require human authority — not because AI isn't smart enough, but because you want explicit sign-off:

```yaml
hitl:
  message: "Consensus finding: SQL injection in auth.py. Deploy fix?"
  options: [deploy, review-first, abort]
  show: raw
```

Skip entirely in automated pipelines with `--ci`:

```bash
polyflow run my-workflow --ci -i "..."   # HITL auto-approves, never blocks
```

### Context Injection

Automatically include project files in prompts:

```yaml
context:
  inject_cwd: true
  inject_files:
    - "src/**/*.py"
    - "README.md"
  max_file_size: 50kb
```

### Error Handling

```yaml
on_error:
  retry: 2
  fallback: continue    # abort | continue | skip
```

Retries use exponential backoff. Rate-limit errors (429) retry automatically; auth errors (401, 403) fail fast.

---

## CLI Reference

```
polyflow list [--tag security]       Browse available workflows
polyflow run <name|path> -i "..."    Run a workflow
polyflow run <name> --ci -i "..."    Run headlessly (no prompts, auto-approve)
polyflow validate <file.yaml>        Validate workflow YAML
polyflow new "description" -o f.yaml Generate from natural language
polyflow pull <name>                 Download from community registry
polyflow search                      List community workflows
polyflow init                        Configure API keys
polyflow doctor                      Check your setup
polyflow schema                      Show full YAML schema reference
```

---

## GitHub Actions

Add three-model consensus to any repo in 30 seconds.

**1. Add to GitHub Secrets** (`Settings → Secrets → Actions`):

| Secret | Description |
|---|---|
| `OPENROUTER_API_KEY` | Covers Claude + Gemini + GPT-4 (recommended) |
| `ANTHROPIC_API_KEY` | Claude only |
| `GOOGLE_API_KEY` | Gemini only |
| `OPENAI_API_KEY` | GPT-4 only |

**2. Copy a workflow file into `.github/workflows/`:**

| File | Trigger | What it does |
|---|---|---|
| [polyflow-code-review.yml](.github/workflows/polyflow-code-review.yml) | Pull request | 3-model parallel review posted as PR comment |
| [polyflow-security-audit.yml](.github/workflows/polyflow-security-audit.yml) | Push to main / weekly | Consensus security audit, opens issue on critical findings |
| [polyflow-pr-description.yml](.github/workflows/polyflow-pr-description.yml) | PR opened | Auto-generates PR description from diff |

**3. That's it.** Every PR now gets reviewed by three AI models simultaneously.

### Custom workflow in Actions

```yaml
- uses: celesteimnskirakira/polyflow@main
  with:
    workflow: ./my-workflow.yaml      # built-in name or local path
    input: ${{ steps.diff.outputs.content }}
    output-file: report.md
    openrouter-api-key: ${{ secrets.OPENROUTER_API_KEY }}
```

### Action inputs / outputs

| Input | Required | Default | Description |
|---|---|---|---|
| `workflow` | ✅ | — | Workflow name or `.yaml` path |
| `input` | | `""` | Input string (`-i` flag) |
| `output-file` | | — | Save output to file |
| `version` | | `latest` | Pin `polyflow-ai` version |
| `openrouter-api-key` | | — | OpenRouter (all models) |
| `anthropic-api-key` | | — | Claude only |
| `google-api-key` | | — | Gemini only |
| `openai-api-key` | | — | GPT-4 only |

| Output | Description |
|---|---|
| `result` | Workflow output text |
| `output-file` | Path to saved output file |

---

## Available Workflows (22 built-in)

| Workflow | Models | Description |
|---|---|---|
| `code-review-multi-model` | Claude + Gemini + GPT-4 | Parallel review, consensus findings |
| `security-audit` | Claude + Gemini | OWASP-based vulnerability analysis |
| `cross-validate` | Claude + Gemini + GPT-4 | Plan → parallel validation → synthesize |
| `bug-triage` | Claude + Gemini | Severity classification + fix suggestions |
| `test-generation` | Claude + GPT-4 | Unit test generation with coverage analysis |
| `pr-description` | Claude | Auto-generate PR descriptions from diffs |
| `feature-spec` | Claude + Gemini | User story → technical specification |
| `adr-generator` | Claude + Gemini | Architecture Decision Record |
| `incident-postmortem` | Claude + GPT-4 | Structured incident analysis |
| `api-documentation` | Claude | OpenAPI documentation generation |
| `database-schema-design` | Claude + Gemini | Schema design with normalization review |
| `deploy-checklist` | Claude + Gemini + GPT-4 | Pre-deployment readiness check |
| `changelog-generator` | Claude | Conventional commit → changelog |
| `dependency-audit` | Claude + Gemini | Vulnerability + license analysis |
| `performance-analysis` | Claude + GPT-4 | Bottleneck identification |
| `microservice-design` | Claude + Gemini | Service boundary design |
| `data-pipeline-design` | Claude + GPT-4 | ETL/streaming architecture |
| `technical-interview` | Claude + GPT-4 | Interview question generation |
| `content-moderation` | Claude + Gemini + GPT-4 | Multi-model policy review |
| `api-spec-design` | Claude + Gemini | REST API spec from requirements |
| `code-refactoring` | Claude + GPT-4 | Refactoring plan with safety analysis |

```bash
polyflow list                    # browse all
polyflow list --tag security     # filter by tag
```

---

## Models

| Alias | Model | Provider |
|---|---|---|
| `claude` | Claude Sonnet 4.6 | Anthropic / OpenRouter |
| `gemini` | Gemini 2.0 Flash | Google / OpenRouter |
| `gpt-4` | GPT-4o | OpenAI / OpenRouter |

**Recommended:** [OpenRouter](https://openrouter.ai) — one API key, all three models, no juggling.

---

## Architecture

```
YAML workflow
    ↓
Pydantic validation (schema/workflow.py)
    ↓
Jinja2-style template engine (engine/template.py)
    ↓
Async executor (engine/executor.py)
    ├── Sequential steps
    ├── Parallel steps → asyncio.gather (true concurrency)
    │     └── Aggregation → vote | diff | summary | raw
    ├── Human-in-the-Loop (optional)
    └── Conditional skip
    ↓
Model adapters (models/)
    ├── OpenRouter (unified — recommended)
    ├── Claude (Anthropic SDK)
    ├── Gemini (google-genai)
    └── GPT-4 (openai)
    ↓
Output saving (markdown | json | text)
```

---

## Contributing

Workflows are plain YAML — no code required.

1. Fork the repo
2. Add your workflow to `workflows/examples/`
3. Validate: `polyflow validate your-workflow.yaml`
4. Open a PR

**The best workflows use at least two models** to demonstrate the cross-validation value. Single-model workflows are fine for sequential pipelines but miss the point of Polyflow.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT — see [LICENSE](LICENSE).
