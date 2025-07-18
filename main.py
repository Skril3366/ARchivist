import click

from src.config import logger, setup_logging


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
@click.argument("chat_export_path", type=click.Path(exists=True))
def analyze(chat_export_path):
    """Analyze a Telegram chat export JSON file."""
    logger.info(f"Analyzing chat export: {chat_export_path}")
    click.echo(f"Starting analysis of {chat_export_path}...")
    # Placeholder for analysis logic
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
