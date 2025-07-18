# Telegram Chat Analyzer

## Overview

The Telegram Chat Analyzer is a Python application that processes Telegram chat JSON exports to extract structured information about users and store it in a local Neo4j graph database. The system uses a local Ollama instance with the Gemma model for AI-powered fact extraction and natural language querying.

## Core Functionality

### Data Processing
- **Input:** Telegram chat JSON exports containing message history
- **Processing:** Analyzes messages using sliding window context to understand conversations
- **Extraction:** Uses AI to identify user facts like names, locations, interests, and other relevant attributes
- **Storage:** Stores extracted information as graph nodes and relationships in Neo4j

### Key Features
- **Resumable Processing:** Can interrupt and resume large chat analysis without losing progress
- **Contextual Understanding:** Uses surrounding messages and reply chains for better fact extraction
- **Dynamic Schema:** Automatically discovers new user attributes while avoiding duplicates
- **Natural Language Queries:** Ask questions in plain English, get structured answers
- **Local Processing:** All AI processing happens locally using Ollama, no external API calls

## Technical Architecture

### Components
- **Message Parser:** Handles Telegram JSON format with robust error handling
- **Context Manager:** Implements sliding window for gathering relevant message context
- **Fact Extractor:** AI-powered extraction of structured user information
- **Graph Database:** Neo4j storage for users, attributes, and relationships
- **Query Engine:** Natural language to Cypher translation for database queries
- **State Management:** Persistent processing state for resumable operations

### Technology Stack
- **Language:** Python 3.13+ (as per .python-version and pyproject.toml)
- **Package Management:** UV for fast, reliable dependency management
- **AI Model:** Local Ollama instance with Gemma model
- **Database:** Neo4j for graph storage and querying
- **CLI:** Click-based command-line interface
- **Logging:** Loguru for structured and easy logging
- **Environment Variables:** Python-dotenv for configuration
- **Task Runner:** Just for simplified command execution
- **Git Hooks:** Custom bash script for automated linting and formatting

## Use Cases

### Personal Chat Analysis
- Understand your social circles and conversation patterns
- Track how relationships and interests evolve over time
- Discover forgotten connections and shared interests

### Group Chat Insights
- Analyze community dynamics and member profiles
- Identify key contributors and conversation topics
- Map relationship networks within groups

### Research Applications
- Study communication patterns in digital communities
- Analyze social network formation and evolution
- Extract demographic and interest data from conversations

## Data Privacy

All processing happens locally on your machine. No chat data is sent to external services, ensuring complete privacy and control over sensitive conversation history.

## Example Queries

- "Who are the users from Amsterdam?"
- "Show me people interested in photography"
- "Find users who mentioned traveling to Japan"
- "What are the most common interests in this chat?"

## Installation Requirements

- Python 3.13 or higher (as per .python-version)
- UV package manager
- Docker and docker-compose
- Local Ollama installation with Gemma model
- Telegram chat JSON export file
- Just command runner

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/telegram-analyzer.git
    cd telegram-analyzer
    ```

2.  **Install UV:**
    If you don't have UV installed, follow the instructions on the [UV GitHub page](https://astral.sh/uv).
    A common way is:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
    Make sure UV is in your PATH.

3.  **Install Just:**
    If you don't have Just installed, follow the instructions on the [Just GitHub page](https://github.com/casey/just).
    A common way is:
    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash
    ```
    Make sure `just` is in your PATH.

4.  **Set up Environment Variables:**
    **Crucial:** Copy the `.env.template` file to `.env` in the root directory of the project (where `docker-compose.yml` is located) and fill in your credentials and API endpoints. Docker Compose automatically looks for a `.env` file in the same directory.
    ```bash
    cp .env.template .env
    # Open .env in your editor and modify:
    # OLLAMA_API_BASE_URL=http://localhost:11434
    # NEO4J_URI=bolt://localhost:7687
    # NEO4J_USERNAME=neo4j
    # NEO4J_PASSWORD=your_neo4j_password
    ```
    **Important:** Change `your_neo4j_password` to a strong, unique password.

5.  **Initial Project Setup:**
    Run the `setup` command using `just`. This will install Python dependencies, prepare the Neo4j data directories with appropriate permissions, and install the Git pre-commit hooks.
    ```bash
    just setup
    ```
    **Troubleshooting Permissions:** If you still encounter "Permission denied" errors (e.g., `chown: changing ownership of '/var/lib/neo4j/import': Permission denied`) when starting Neo4j, ensure the `chmod -R 777 data` command executed by `just setup` was successful. You might need to manually run `sudo chmod -R 777 data` if your system's permissions are particularly restrictive.

6.  **Start Neo4j Database (using Docker):**
    Ensure Docker and Docker Compose are installed and running on your system.
    ```bash
    just start-neo4j
    ```
    This will start a Neo4j container in the background. Data will be persisted in the `./data/neo4j` directory.

7.  **Install Ollama and Download Gemma Model:**
    Follow the instructions on the [Ollama website](https://ollama.ai/download) to install Ollama.
    Once Ollama is running, download the Gemma model:
    ```bash
    ollama run gemma:2b
    # Or for a larger model:
    # ollama run gemma:7b
    ```
    Ensure Ollama is running and accessible at the `OLLAMA_API_BASE_URL` specified in your `.env` file.

## Usage

All common commands are available via the `just` command runner.

*   **List all available commands:**
    ```bash
    just --list
    ```

*   **Say hello:**
    ```bash
    just hello
    ```

*   **Analyze a chat export:**
    By default, the `analyze` command looks for `data/telegram_dump.json`.
    ```bash
    # Analyze the default file: data/telegram_dump.json
    just analyze
    ```
    You can also specify a custom path:
    ```bash
    # Analyze a specific file
    just analyze /path/to/your/custom_telegram_export.json
    ```

*   **Query analyzed data (placeholder):**
    ```bash
    just query "Who are the users from Amsterdam?"
    ```

*   **Start Neo4j:**
    ```bash
    just start-neo4j
    ```

*   **Stop Neo4j:**
    ```bash
    just stop-neo4j
    ```

*   **Run tests:**
    ```bash
    just test
    ```

*   **Run linter:**
    ```bash
    just lint
    ```

*   **Format code:**
    ```bash
    just format
    ```

*   **Clean up generated files and data directories:**
    ```bash
    just clean
    ```

## Git Hooks (Manual Setup)

This project uses a custom Git `pre-commit` hook to automatically run `ruff format` and `ruff check` before every commit.

*   **Installation:** The `just setup` command automatically installs this custom `pre-commit` hook. If you need to install it manually later, run:
    ```bash
    just install-hooks
    ```
*   **Usage:** Once installed, simply commit your changes as usual:
    ```bash
    git add .
    git commit -m "Your commit message"
    ```
    The `pre-commit` hook will automatically run the configured checks on staged Python files.
    *   If `ruff format` makes any changes, it will apply them, and the commit will be aborted. You will need to `git add` the newly formatted files and commit again.
    *   If `ruff check` finds any linting errors, the commit will be aborted, allowing you to fix them.

## Project Structure

```
telegram-analyzer/
├── src/
│   ├── config.py        # Configuration and logging setup
│   ├── models/          # Data models and schemas
│   ├── parsers/         # Telegram JSON parsing
│   ├── processing/      # Context management and pipeline
│   ├── extraction/      # AI-powered fact extraction
│   ├── database/        # Neo4j interface
│   ├── query/           # Natural language querying
│   └── llm/             # LLM provider abstraction
├── tests/               # Comprehensive test suite
├── docs/                # Documentation and examples
├── data/                # Persistent data for Neo4j and default Telegram dump location
├── logs/                # Application logs
├── scripts/             # Helper scripts (e.g., Git hooks)
│   └── pre-commit.sh    # Custom pre-commit hook script
├── .env.template        # Template for environment variables
├── docker-compose.yml   # Docker Compose configuration for Neo4j
├── Justfile             # Just command runner configuration
├── pyproject.toml       # UV project configuration
└── main.py              # CLI entry point
```

## Development Philosophy

The application follows modern Python best practices with emphasis on:
- **Modularity:** Clean separation of concerns
- **Robustness:** Comprehensive error handling and recovery
- **Extensibility:** Easy to add new features and providers
- **Performance:** Efficient processing of large chat histories
- **Maintainability:** Well-documented, tested code
- **Tooling:** Leveraging `uv` for package management, `ruff` for linting and formatting, `loguru` for logging, `just` for task automation, and custom Git hooks for code quality enforcement.
