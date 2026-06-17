# Contributing

Thanks for considering a contribution.

## Development

```bash
pip install -e .
python -m pytest -q
```

Keep the package local-first and dependency-light. Do not add network calls, telemetry, or hosted services unless they are optional and documented.

## Pull Requests

- Include tests for behavior changes.
- Keep user-facing strings in all bundled locales.
- Do not commit local databases, notebook data, `.env` files, or credentials.
- Run `python -m pytest -q` before opening a pull request.
