# Contributing

Thanks for considering a contribution.

## Development

```bash
pip install -e .
python -m pip install pytest build ruff
ruff check llm_note tests
python -m pytest -q
python -m build
```

Keep the package local-first and dependency-light. Do not add network calls, telemetry, or hosted services unless they are optional and documented.

## Pull Requests

- Include tests for behavior changes.
- Keep user-facing strings in all bundled locales.
- Do not commit local databases, notebook data, `.env` files, or credentials.
- Run lint, tests, and a clean package build before opening a pull request.
