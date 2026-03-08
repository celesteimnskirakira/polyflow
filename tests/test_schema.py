import pytest
import yaml
from polyflow.schema.workflow import Workflow, Step, ParallelStep, HitlConfig


def test_minimal_workflow_parses():
    raw = yaml.safe_load("""
name: test-flow
version: "1.0"
steps:
  - id: step1
    name: First Step
    model: claude
    prompt: "Hello {{input}}"
""")
    wf = Workflow.model_validate(raw)
    assert wf.name == "test-flow"
    assert len(wf.steps) == 1
    assert wf.steps[0].id == "step1"


def test_parallel_step_parses():
    raw = yaml.safe_load("""
name: parallel-flow
version: "1.0"
steps:
  - id: validate
    name: Validate
    type: parallel
    steps:
      - id: gemini
        model: gemini
        prompt: "Review: {{steps.prev.output}}"
      - id: gpt4
        model: gpt-4
        prompt: "Review: {{steps.prev.output}}"
    aggregate:
      mode: diff
      model: claude
""")
    wf = Workflow.model_validate(raw)
    step = wf.steps[0]
    assert step.type == "parallel"
    assert len(step.steps) == 2
    assert step.aggregate.mode == "diff"


def test_hitl_config_parses():
    raw = yaml.safe_load("""
name: hitl-flow
version: "1.0"
steps:
  - id: review
    name: Review
    model: claude
    prompt: "Review this"
    hitl:
      message: "Confirm?"
      options: [continue, abort, revise]
      timeout: 10m
""")
    wf = Workflow.model_validate(raw)
    hitl = wf.steps[0].hitl
    assert hitl.message == "Confirm?"
    assert "revise" in hitl.options


def test_missing_name_raises():
    raw = {"version": "1.0", "steps": []}
    with pytest.raises(Exception):
        Workflow.model_validate(raw)
