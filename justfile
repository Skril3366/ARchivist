# Justfile for Telegram Chat Analyzer

# Use bash for executing commands for better consistency
set shell := ["bash", "-c"]

# Variables
# Define the path to the main Python script
PYTHON_MAIN := "main.py"

# Setup commands
setup: install-deps setup-neo4j-dirs install-hooks
    @echo "Setup complete. You can now run 'just start-neo4j' and 'just hello'."

install-deps:
    @echo "Installing Python dependencies..."
    uv pip install .
    uv pip install '.[dev]'

setup-neo4j-dirs:
    @echo "Creating Neo4j data directories and setting permissions..."
    mkdir -p data/neo4j/data
    mkdir -p data/neo4j/import
    mkdir -p data/neo4j/logs
    mkdir -p data/neo4j/plugins
    mkdir -p data # Ensure data directory for telegram_dump.json exists
    # Grant full permissions for development to avoid Docker permission issues.
    # For production, consider more restrictive permissions and chown to UID/GID 7474.
    chmod -R 777 data
    @echo "Neo4j data directories created and permissions set."

install-hooks:
    @echo "Installing Git pre-commit hooks..."
    mkdir -p .git/hooks
    cp scripts/pre-commit.sh .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    @echo "Pre-commit hooks installed. Formatting and linting will run automatically before each commit."

# Docker Compose commands
start-neo4j:
    @echo "Starting Neo4j database..."
    docker-compose up -d neo4j

stop-neo4j:
    @echo "Stopping Neo4j database..."
    docker-compose down

# Application commands
hello:
    @echo "Running hello command..."
    uv run python "{{PYTHON_MAIN}}" hello

analyze *CHAT_EXPORT_PATH:
    @echo "Running analyze command..."
    uv run python "{{PYTHON_MAIN}}" analyze {{CHAT_EXPORT_PATH}}

reset-state:
    @echo "Resetting processing state..."
    uv run python "{{PYTHON_MAIN}}" reset-state

query QUERY_TEXT:
    @echo "Running query command for '$(QUERY_TEXT)'..."
    uv run python "{{PYTHON_MAIN}}" query "{{QUERY_TEXT}}"

# Development commands
test:
    @echo "Running tests..."
    uv run pytest

lint:
    @echo "Running linter (ruff check)..."
    uv run ruff check src/ main.py

format:
    @echo "Running formatter (ruff format)..."
    uv run ruff format src/ main.py

# Clean command
clean:
    @echo "Cleaning up generated files and directories..."
    rm -rf __pycache__/ .pytest_cache/ .ruff_cache/ logs/ uv.lock
    rm -rf data/neo4j/data data/neo4j/import data/neo4j/logs data/neo4j/plugins
    @echo "Cleanup complete."
