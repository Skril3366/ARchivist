#!/bin/bash

# This script is a custom Git pre-commit hook.
# It runs ruff format and ruff check on staged Python files.

# Get a list of staged Python files
# --cached: only consider files in the index (staged)
# --name-only: show only the names of changed files
# --diff-filter=ACM: include Added, Copied, Modified files (exclude Deleted)
STAGED_PYTHON_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -z "$STAGED_PYTHON_FILES" ]; then
    echo "No Python files staged. Skipping formatting and linting."
    exit 0
fi

echo "Running ruff format on staged Python files..."
# Run ruff format on staged files. Ruff will modify files in place.
# We use 'uv run' to ensure ruff is executed within the project's virtual environment.
uv run ruff format $STAGED_PYTHON_FILES

# Check if ruff format made any changes to staged files that are still staged
# If there are differences, it means ruff formatted files that were already staged.
# The user needs to 'git add' these changes before committing.
if ! git diff --quiet --exit-code --cached; then
    echo "Ruff format made changes to staged files. Please 'git add .' the changes and commit again."
    exit 1
fi

echo "Running ruff check on staged Python files..."
# Run ruff check on staged files.
uv run ruff check $STAGED_PYTHON_FILES

# Check the exit code of ruff check
if [ $? -ne 0 ]; then
    echo "Ruff check found issues. Please fix them before committing."
    exit 1
fi

echo "Pre-commit checks passed."
exit 0
