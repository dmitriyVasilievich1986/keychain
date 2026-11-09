# Backend Agent Instructions

These instructions apply to everything under `backend/`. Project-level architecture is documented in the repository's top-level `AGENTS.md`; this file only covers backend-specific tooling and code style rules.

## Package Management

- `uv` is the only supported package manager and executor for this backend. Never use `pip`, `poetry`, `python -m venv`, or a bare `python` invocation.
- Every `uv run` invocation must include `--env-file=.env`, e.g.:
  ```bash
  uv run --env-file=.env pytest
  uv run --env-file=.env ruff check .
  uv run --env-file=.env keychain <command>
  ```
- Add dependencies with `uv add <package>` (or `uv add --group dev <package>` for dev-only tools) instead of editing `pyproject.toml` by hand.
- Sync the environment with `uv sync` after pulling changes that touch `pyproject.toml` or `uv.lock`.

## Docstrings

- Every module, class, and method/function must have a docstring written in Google docstring format (`Args:`, `Returns:`, `Raises:` sections as applicable).
- Keep docstrings accurate and up to date with the signature; do not describe implementation details that are better left to the code itself.

## Type Annotations

- All function and method arguments must be typed, including `self`/`cls` exclusions as usual. Return types must be annotated as well.
- Use precise types from `typing`, the standard library, or project models rather than `Any`, unless there is no narrower type available.

## Linting and Formatting

- All code must pass `ruff` using the configuration in `backend/pyproject.toml` (`[tool.ruff]`), including the enabled rule sets (`A`, `ARG`, `ASYNC`, `PTH`, `B`, `E`, `F`, `N`, `W`, `RUF`, `SLF`, `RET`, `Q`, `T20`, `COM`, `D`, `FIX`, plus `I` import sorting).
- Run lint and format checks via `uv`:
  ```bash
  uv run --env-file=.env ruff check .
  uv run --env-file=.env ruff format .
  ```
- Fix lint violations rather than suppressing them with `# noqa` unless there is no reasonable alternative.

## Tests

- Run the test suite via `uv run --env-file=.env pytest` before considering backend work complete.
