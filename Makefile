ruff_format:
	uv run ruff format

ruff_check:
	uv run ruff check --fix

mypy:
	uv run mypy ./keychain

format: ruff_format ruff_check mypy
