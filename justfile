_default:
  just --list


# Install the project dependencies
install:
    uv sync --all-extras

# Format the code and check for linting issues
linting:
    pre-commit run --all-files

typecheck:
    uv run mypy

# Run unit tests
test: install
    uv run pytest
