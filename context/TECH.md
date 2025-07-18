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
- **Language:** Python 3.9+
- **Package Management:** UV for fast, reliable dependency management
- **AI Model:** Local Ollama instance with Gemma model
- **Database:** Neo4j for graph storage and querying
- **CLI:** Click-based command-line interface

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

- Python 3.9 or higher
- UV package manager
- Docker and docker-compose
- Local Ollama installation with Gemma model
- Telegram chat JSON export file

## Project Structure

```
telegram-analyzer/
├── src/
│   ├── models/          # Data models and schemas
│   ├── parsers/         # Telegram JSON parsing
│   ├── processing/      # Context management and pipeline
│   ├── extraction/      # AI-powered fact extraction
│   ├── database/        # Neo4j interface
│   ├── query/           # Natural language querying
│   └── llm/             # LLM provider abstraction
├── tests/               # Comprehensive test suite
├── docs/                # Documentation and examples
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
