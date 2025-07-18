from datetime import datetime
from pathlib import Path

import click

from src.config import logger, setup_logging
from src.parsers.telegram_parser import TelegramChatParser
from src.state.processor_state import ProcessingState


@click.group()
@click.pass_context
def cli(ctx):
    """Telegram Chat Analyzer CLI."""
    # Initialize logger only if a subcommand is being invoked.
    # This prevents logs from appearing when --help is called or no command is given.
    if ctx.invoked_subcommand is not None:
        setup_logging()
        logger.info("CLI application started.")
    pass


@cli.command()
def hello():
    """Says hello from archivist."""
    logger.info("Hello command executed.")
    click.echo("Hello from archivist!")


@cli.command()
@click.argument("chat_export_path", type=click.Path(exists=True), required=False)
def analyze(chat_export_path):
    """Analyze a Telegram chat export JSON file.

    If CHAT_EXPORT_PATH is not provided, it defaults to 'data/telegram_dump.json'.
    """
    if not chat_export_path:
        chat_export_path = "data/telegram_dump.json"
        logger.info(f"No chat export path provided, defaulting to {chat_export_path}")
        # Check if the default file exists
        if not click.Path(exists=True).convert(chat_export_path, None, None):
            logger.error(f"Default chat export file not found: {chat_export_path}")
            click.echo(f"Error: Default chat export file not found at '{chat_export_path}'.")
            click.echo("Please place your Telegram dump at this location or specify the path as an argument.")
            return

    logger.info(f"Analyzing chat export: {chat_export_path}")
    click.echo(f"Starting analysis of {chat_export_path}...")

    state_file = Path("data/processing_state.json")
    state = ProcessingState.load(state_file)

    if state and state.chat_export_path != Path(chat_export_path):
        logger.warning(
            f"Chat export path in state ({state.chat_export_path}) does not match current path ({chat_export_path})."
        )
        if click.confirm("Do you want to reset the processing state and start a new analysis for this file?"):
            state.reset()
            state.chat_export_path = Path(chat_export_path)  # Set new path after reset
            click.echo("Processing state reset confirmed.")
        else:
            click.echo(
                "Analysis aborted. Please provide the correct chat export path or "
                "reset the state manually using 'just reset-state'."
            )
            return
    elif not state:
        state = ProcessingState(chat_export_path=Path(chat_export_path))

    state.status = "in_progress"
    if not state.start_time:
        state.start_time = datetime.now().isoformat()
    state.save(state_file)

    try:
        parser = TelegramChatParser(chat_export_path)
        chat = parser.load_and_validate()
        click.echo(f"Successfully loaded chat: '{chat.name}' with {len(chat.messages)} messages.")

        # Find the starting point for processing
        start_index = 0
        if state.last_processed_message_id > 0:
            # Attempt to find the index of the last processed message + 1
            # This assumes messages are sorted by ID in the export
            found_last_processed = False
            for i, msg in enumerate(chat.messages):
                if msg.id == state.last_processed_message_id:
                    start_index = i + 1
                    found_last_processed = True
                    break
            if not found_last_processed:
                logger.warning(
                    f"Last processed message ID {state.last_processed_message_id} not found in current export."
                )
                click.echo(
                    "Warning: The last processed message ID from the saved state was not found "
                    "in the current chat export."
                )
                click.echo("This might indicate a different export file or a reordered export.")
                click.echo(
                    "Analysis will start from the beginning. If this is not desired, please reset "
                    "the state manually using 'just reset-state' and try again."
                )
                start_index = 0  # Start from beginning if not found, but don't reset state automatically

        messages_to_process = chat.messages[start_index:]
        if start_index > 0:
            click.echo(
                f"Resuming analysis from message ID {state.last_processed_message_id + 1} "
                f"({len(messages_to_process)} messages remaining)."
            )
        else:
            click.echo(f"Starting new analysis. Processing {len(messages_to_process)} messages.")

        for message in messages_to_process:
            logger.info(f"Processing message {message.id} (Type: {message.type}) from {message.from_name}")
            # In a real scenario, you would add your processing logic here
            # e.g., extract facts, store in Neo4j, etc.

            state.last_processed_message_id = message.id
            state.total_messages_processed += 1
            state.save(state_file)  # Save state after each message or in batches

        state.status = "completed"
        state.end_time = datetime.now().isoformat()
        state.save(state_file)
        click.echo(f"Analysis completed. Total messages processed: {state.total_messages_processed}.")

    except FileNotFoundError:
        # Error message already logged by the CLI argument check or parser
        state.status = "failed"
        state.end_time = datetime.now().isoformat()
        state.save(state_file)
        pass
    except Exception as e:
        logger.error(f"An error occurred during analysis: {e}")
        click.echo("An error occurred during analysis. Check logs for details.")
        state.status = "failed"
        state.end_time = datetime.now().isoformat()
        state.save(state_file)

    click.echo("Analysis complete (placeholder).")


@cli.command()
def reset_state():
    """Reset the processing state, allowing analysis to start from scratch."""
    state_file = Path("data/processing_state.json")
    state = ProcessingState.load(state_file)
    if state:
        state.reset()
        state.save(state_file)
        click.echo("Processing state has been reset.")
    else:
        click.echo("No processing state found to reset.")


@cli.command()
@click.argument("query_text")
def query(query_text):
    """Query the analyzed chat data using natural language."""
    logger.info(f"Executing query: {query_text}")
    click.echo(f"Executing query: '{query_text}'...")
    # Placeholder for query logic
    click.echo("Query results (placeholder).")


if __name__ == "__main__":
    cli()
