# Contributing to Polyflow

## Adding a Workflow

The easiest way to contribute is adding a new workflow to `workflows/examples/`.

**Steps:**
1. Fork the repository
2. Create `workflows/examples/your-workflow-name.yaml`
3. Validate it: `polyflow validate workflows/examples/your-workflow-name.yaml`
4. Test it with a real input
5. Open a pull request

**Workflow conventions:**
- Use lowercase kebab-case for filenames
- Include `name`, `description`, `version`, and `tags`
- Add a `tags` field so users can filter with `polyflow list --tag <tag>`
- Make prompts detailed and reusable (use `{{input}}` for user-provided content)
- Test with multiple models if using parallel steps

**Example tags:** `code-review`, `security`, `documentation`, `testing`, `design`, `ops`, `data`

## Reporting Bugs

Open an issue at https://github.com/celesteimnskirakira/polyflow/issues

Include:
- Your Polyflow version (`polyflow --version`)
- Output of `polyflow doctor`
- The workflow YAML (if applicable)
- The full error message

## Development Setup

```bash
git clone https://github.com/celesteimnskirakira/polyflow
cd polyflow
pip install -e ".[dev]"

# Run tests (unit tests, no API key needed)
pytest tests/test_config.py tests/test_executor.py tests/test_schema.py tests/test_template.py

# Run integration tests (requires OPENROUTER_API_KEY)
pytest tests/test_integration.py
```

## Code Style

- Python 3.11+, type hints throughout
- `from __future__ import annotations` in all modules
- Pydantic v2 for schema validation
- `asyncio` for all I/O operations
- Rich for terminal output
