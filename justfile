alias fmt := format

_default:
  just --list


# Install the project dependencies
install:
    uv sync --all-extras

# Format the code and check for linting issues
format:
    pre-commit run --all-files

typecheck:
    uv run mypy

# Run unit tests
test: install
    uv run pytest
