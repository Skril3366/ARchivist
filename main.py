import click

from src.config import logger, setup_logging
from src.parsers.telegram_parser import TelegramChatParser


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

    try:
        parser = TelegramChatParser(chat_export_path)
        chat = parser.load_and_validate()
        click.echo(f"Successfully loaded chat: '{chat.name}' with {len(chat.messages)} messages.")

        # Iterate through all messages
        for i, message in enumerate(parser.get_messages()):
            logger.info(f"Processing message {message.id} (Type: {message.type}) from {message.from_name}")

    except FileNotFoundError:
        # Error message already logged by the CLI argument check or parser
        pass
    except Exception as e:
        logger.error(f"An error occurred during analysis: {e}")
        click.echo("An error occurred during analysis. Check logs for details.")

    click.echo("Analysis complete (placeholder).")


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
