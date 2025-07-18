# Telegram Chat Analyzer Engineering Tasks

## Task 1: Project Setup and Dependencies
**Objective:** Create the basic project structure and install required dependencies using UV.

**Details:**
- Create a new Python project directory with modern structure (src/, tests/, docs/, pyproject.toml)
- Initialize UV project with `uv init` and configure pyproject.toml with project metadata
- Add core dependencies using UV: neo4j, requests (for Ollama API), pydantic, click, python-dotenv, pytest
- Create docker-compose.yml for Neo4j container with authentication and persistent volumes
- Create a basic .env template file for Ollama endpoint, Neo4j credentials, and Docker settings
- Set up basic logging configuration with structured logging
- Create a main.py entry point with basic CLI structure using click
- Add UV scripts configuration in pyproject.toml for common commands
- Include Docker setup instructions and container management helpers

**Verification:** Project structure exists, `uv install` completes successfully, `docker-compose up` starts Neo4j successfully, main.py runs with --help flag

## Task 2: Define Core Data Models
**Objective:** Create dataclasses and enums for representing Telegram messages and user facts.

**Details:**
- Create `models/message.py` with dataclasses for TelegramMessage, TextEntity, MessageReaction
- Create `models/user.py` with dataclasses for UserFact, UserProfile containing required fields (real_name, city, interests) and dynamic fields dictionary
- Create `models/enums.py` with enums for MessageType, EntityType, ActionType based on Telegram schema
- Include proper type hints and validation using pydantic or dataclasses with validation
- Add methods for serialization/deserialization to/from JSON

**Verification:** All models can be instantiated, serialized to JSON, and deserialized back without data loss

## Task 3: JSON Message Parser
**Objective:** Create a robust parser for Telegram JSON dump files.

**Details:**
- Create `parsers/telegram_parser.py` with TelegramChatParser class
- Implement method to load and validate JSON structure (check for required top-level fields)
- Implement iterator pattern for processing messages one by one or in batches
- Handle both string and array formats for text fields
- Add comprehensive error handling for malformed JSON or missing fields
- Include progress tracking capabilities
- **The parser should be able to read from `data/telegram_dump.json` by default, or from a path specified by the user via CLI.**

**Verification:** Parser can load sample Telegram JSON files, iterate through messages, and handle various text formats correctly

## Task 4: Processing State Management
**Objective:** Implement resumable processing with persistent state tracking.

**Details:**
- Create `state/processor_state.py` with ProcessingState dataclass
- Implement methods to save/load state to/from JSON file
- Track: last processed message ID, accumulated user facts, processing statistics
- Include atomic write operations to prevent state corruption
- Add method to reset state for fresh processing runs
- Implement state validation to detect corrupted state files

**Verification:** State can be saved, loaded, and survives application restarts while maintaining processing continuity

## Task 5: Sliding Window Context Manager
**Objective:** Implement context window management for gathering relevant messages around target messages.

**Details:**
- Create `processing/context_manager.py` with SlidingWindowContext class
- Implement method to extract N messages before and after target message
- Add reply chain following to include replied-to messages in context
- Handle edge cases (start/end of chat, missing reply targets)
- Include user-specific message filtering for focused context
- Add configurable window size and depth parameters

**Verification:** Context manager returns appropriate message windows and handles edge cases without errors

## Task 6: LLM Interface Layer
**Objective:** Create abstraction layer for LLM interactions with Ollama integration and extensible provider system.

**Details:**
- Create `llm/llm_interface.py` with abstract LLMProvider base class defining standard interface methods
- Implement `llm/ollama_provider.py` with OllamaProvider class for local Ollama integration
- Configure for Gemma model by default with model selection capability
- Create `llm/prompts.py` with structured prompts optimized for Gemma's capabilities
- Add retry logic, connection handling, and error recovery for local Ollama instance
- Include response parsing and validation specific to Gemma's output format
- Add model warmup and health check methods for the local instance
- Design provider factory pattern for easy future extension to other providers

**Verification:** Ollama provider can successfully communicate with local instance, send prompts, and return structured responses with proper error handling

## Task 7: Fact Extraction Engine
**Objective:** Implement the core logic for extracting user facts from message contexts.

**Details:**
- Create `extraction/fact_extractor.py` with UserFactExtractor class
- Implement method to analyze message context and extract structured facts
- Add semantic similarity checking to avoid duplicate attributes
- Include confidence scoring for extracted facts
- Implement fact merging logic for combining information from multiple messages
- Add validation to ensure extracted facts match expected schema

**Verification:** Fact extractor can process message contexts and return structured, deduplicated user facts

## Task 8: Neo4j Database Interface
**Objective:** Create database layer for storing and retrieving user facts in Neo4j with Docker integration.

**Details:**
- Create `database/neo4j_interface.py` with Neo4jManager class
- Add `docker-compose.yml` for Neo4j container with proper volumes and authentication
- Implement connection management with retry logic and health checks
- Add methods for creating/updating user nodes with dynamic properties
- Include index creation for common query patterns
- Add transaction support for atomic operations
- Create database initialization scripts for constraints and indexes

**Verification:** Database interface can connect to dockerized Neo4j, create/update nodes, and handle connection failures gracefully

## Task 9: Natural Language Query System
**Objective:** Implement natural language to Cypher query translation and execution.

**Details:**
- Create `query/nl_query_processor.py` with NLQueryProcessor class
- Implement method to translate natural language to Cypher using LLM
- Add query validation and sanitization to prevent injection attacks
- Include result formatting for user-friendly output
- Add query caching for common patterns
- Implement query explanation feature for debugging

**Verification:** Query processor can translate natural language questions to valid Cypher and return formatted results

## Task 10: Main Processing Pipeline
**Objective:** Create the main orchestration logic that ties all components together.

**Details:**
- Create `core/pipeline.py` with TelegramAnalyzerPipeline class
- Implement main processing loop with batch processing capabilities
- Add progress tracking and logging throughout the pipeline
- Include error recovery mechanisms for each processing stage
- Implement graceful shutdown handling
- Add configuration management for all pipeline parameters

**Verification:** Pipeline can process complete Telegram JSON dumps from start to finish with proper error handling

## Task 11: Command Line Interface
**Objective:** Create user-friendly CLI for running analysis and queries.

**Details:**
- Enhance main.py with comprehensive CLI commands using click
- Add commands for: analyze (process JSON), query (natural language), status (show progress), reset (clear state)
- Include configuration options for batch size, window size, LLM provider
- Add progress bars and real-time status updates
- Implement configuration file support for default settings

**Verification:** CLI provides intuitive interface for all major operations with helpful error messages

## Task 12: Testing Framework
**Objective:** Implement comprehensive tests for all major components.

**Details:**
- Create unit tests for all data models and validation logic
- Add integration tests for database operations and LLM interactions
- Create test fixtures with sample Telegram JSON data
- Implement end-to-end tests for complete processing pipeline
- Add performance tests for large dataset processing
- Include test coverage reporting

**Verification:** All tests pass and provide adequate coverage of critical functionality

## Task 13: Documentation and Examples
**Objective:** Create comprehensive documentation and usage examples with UV, Ollama, and Docker setup instructions.

**Details:**
- Write README.md with UV-based installation and setup instructions
- Include step-by-step Ollama installation and Gemma model setup guide
- Add Docker and docker-compose setup instructions for Neo4j
- Create API documentation for all public classes and methods
- Add example Telegram JSON files for testing and demonstration
- Write usage examples for common query patterns and workflows
- Include troubleshooting guide for common Ollama, Neo4j, and Docker issues
- Add performance tuning recommendations for local model usage
- Create development setup guide using UV virtual environments and Docker services

**Verification:** Documentation enables new users to successfully install UV, set up Ollama with Gemma, start Neo4j with Docker, and run the complete system

## Task 14: Performance Optimization and Monitoring
**Objective:** Add performance monitoring and optimization features.

**Details:**
- Implement performance metrics collection (processing speed, memory usage, API calls)
- Add configurable batch processing with optimal batch sizes
- Include memory usage monitoring and garbage collection optimization
- Add performance profiling capabilities
- Implement adaptive processing based on system resources
- Create performance dashboard or reporting

**Verification:** System includes performance monitoring and can process large datasets efficiently without memory issues
