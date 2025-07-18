import os
import sys

from dotenv import dotenv_values
from loguru import logger

# Load environment variables from .env file
# This will load variables from .env in the current directory
# or any parent directory.
env_vars = dotenv_values()

# Remove default handler to prevent immediate output upon import
logger.remove()


def setup_logging():
    """Configure the Loguru logger with file and console handlers.

    This function should be called explicitly when logging is desired.
    """
    # Ensure logs directory exists before configuring logger to write to it
    os.makedirs("logs", exist_ok=True)

    # Add file handler (all INFO messages and above go to file)
    logger.add(
        "logs/file_{time}.log",
        rotation="10 MB",
        compression="zip",
        level="INFO",
        format="{time} {time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {file}:{line: <4} | {message}",
        enqueue=True,  # Use a queue for logging to avoid blocking
    )
    # Add console handler (only ERROR messages and above go to console)
    logger.add(
        sys.stderr, level="ERROR", format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {file}:{line: <4} | {message}"
    )
    # Removed specific info logs from here, as they will now only appear in the file log
    # logger.info("Logger initialized.")
    # logger.info(f"Neo4j URI: {NEO4J_URI}")
    # logger.info(f"Ollama API Base URL: {OLLAMA_API_BASE_URL}")


# Database Configuration
NEO4J_URI = env_vars.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = env_vars.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = env_vars.get("NEO4J_PASSWORD", "password")

# Ollama Configuration
OLLAMA_API_BASE_URL = env_vars.get("OLLAMA_API_BASE_URL", "http://localhost:11434")
