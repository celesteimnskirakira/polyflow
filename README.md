# Polyflow

**Multi-model AI workflow engine for developers.** Define, run, and share repeatable AI workflows in YAML — combining Claude, Gemini, and GPT-4 with human-in-the-loop checkpoints.

## Install

```bash
pip install polyflow
```

## Quick Start

```bash
# 1. Configure your API keys
polyflow init

# 2. Browse community workflows
polyflow search

# 3. Pull and run a workflow
polyflow pull cross-validate
polyflow run cross-validate.yaml -i "build a REST API with FastAPI"

# 4. Generate your own workflow from a description
polyflow new "Claude drafts, Gemini reviews, I approve" -o my-flow.yaml
polyflow run my-flow.yaml -i "add user authentication"
```

## Example Workflow

```yaml
name: cross-validate
description: "Claude generates a plan, Gemini and GPT-4 validate it in parallel"
version: "1.0"

steps:
  - id: generate
    name: Generate Plan
    model: claude
    prompt: "Create an implementation plan for: {{input}}"
    hitl:
      message: "Plan ready. Continue to cross-validate?"
      options: [continue, abort]

  - id: validate
    name: Cross-Validate
    type: parallel
    steps:
      - id: gemini
        model: gemini
        prompt: "Review this plan: {{steps.generate.output}}"
      - id: gpt4
        model: gpt-4
        prompt: "Review this plan: {{steps.generate.output}}"
    aggregate:
      mode: diff

  - id: synthesize
    name: Synthesize Final Plan
    model: claude
    prompt: |
      Original: {{steps.generate.output}}
      Feedback: {{steps.validate.output}}
      Synthesize an improved final plan.
```

## Features

- **Multi-model**: Claude, Gemini, GPT-4 in one workflow
- **Parallel execution**: Run multiple models simultaneously, aggregate results
- **Human-in-the-loop**: Confirm, revise, or abort at any step
- **Template engine**: `{{input}}`, `{{steps.id.output}}`, `{{vars.key}}` with pipe fallback
- **Community registry**: Share and pull workflows with `polyflow pull <name>`
- **NL→YAML**: Generate workflows from natural language with `polyflow new`

## Workflow Schema

| Field | Description |
|---|---|
| `name` | Workflow identifier |
| `steps` | List of sequential or parallel steps |
| `steps[].model` | `claude`, `gemini`, or `gpt-4` |
| `steps[].prompt` | Prompt template with `{{...}}` expressions |
| `steps[].hitl` | Human-in-the-loop checkpoint config |
| `steps[].type: parallel` | Run sub-steps concurrently |
| `steps[].aggregate` | How to combine parallel results (`diff`, `vote`, `summary`, `raw`) |

## Config

API keys are stored in `~/.polyflow/config.yaml`:

```yaml
api_keys:
  claude: sk-ant-...
  gemini: AIza...
  gpt-4: sk-...
```

## Community Registry

Browse and contribute workflows at: [polyflow-community/workflows](https://github.com/polyflow-community/workflows)

## License

MIT
