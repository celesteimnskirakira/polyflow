#!/usr/bin/env python3
"""
Standalone Polyflow workflow validator.
Checks required fields without needing the polyflow package installed.
"""
import sys
import yaml

REQUIRED_TOP = {"name", "steps"}
VALID_MODELS = {"claude", "gemini", "gpt-4", "codex"}


def validate(path: str) -> list[str]:
    errors = []
    try:
        with open(path) as f:
            raw = yaml.safe_load(f)
    except Exception as e:
        return [f"YAML parse error: {e}"]

    if not isinstance(raw, dict):
        return ["File is not a YAML mapping"]

    for field in REQUIRED_TOP:
        if field not in raw:
            errors.append(f"Missing required field: '{field}'")

    if "steps" in raw:
        steps = raw["steps"]
        if not isinstance(steps, list) or len(steps) == 0:
            errors.append("'steps' must be a non-empty list")
        else:
            for i, step in enumerate(steps):
                prefix = f"steps[{i}]"
                if not isinstance(step, dict):
                    errors.append(f"{prefix}: must be a mapping")
                    continue
                if "id" not in step:
                    errors.append(f"{prefix}: missing 'id'")
                if "name" not in step:
                    errors.append(f"{prefix}: missing 'name'")
                stype = step.get("type", "sequential")
                if stype == "parallel":
                    if "steps" not in step or not step["steps"]:
                        errors.append(f"{prefix}: parallel step requires 'steps' list")
                elif "model" not in step:
                    errors.append(f"{prefix}: missing 'model' (use: claude, gemini, gpt-4)")

    tags = raw.get("tags", [])
    if not isinstance(tags, list):
        errors.append("'tags' must be a list")

    return errors


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_workflow.py <file.yaml>")
        sys.exit(1)

    failed = 0
    for path in sys.argv[1:]:
        errs = validate(path)
        if errs:
            print(f"✗ {path}")
            for e in errs:
                print(f"  • {e}")
            failed += 1
        else:
            print(f"✓ {path}")

    sys.exit(1 if failed else 0)
