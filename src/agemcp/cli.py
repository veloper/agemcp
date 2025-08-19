"""
agemcp.cli
----------

Command-line interface for the AGE MCP server, providing commands to run and manage the server.

This module uses Click for CLI parsing and Rich for enhanced console output.
"""

import os

import click

from rich.console import Console
from rich.traceback import install as install_traceback

from agemcp.settings import get_settings


console = Console()
install_traceback(show_locals=True, word_wrap=True, console=console)

SETTINGS = get_settings()



@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    Entry point for the AGE MCP CLI.

    Initializes the CLI group, allowing subcommands to be registered.

    Args:
        ctx (click.Context): Click context object for command chaining and configuration.
    """

@cli.command()
def settings() -> None:
    """Show all settings."""
    console.print(SETTINGS.model_dump_json(indent=4))


@cli.command()
@click.option('--port', default=SETTINGS.mcp.port, help='Port to run the server on.')
@click.option('--host', default=SETTINGS.mcp.host, help='Host to run the server on.')
@click.option('--transport', type=click.Choice(['sse', 'streamable-http', 'stdio']), help='Transport to use.', default=SETTINGS.mcp.transport)
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']), default=SETTINGS.mcp.log_level, help='Log level to use.')
def run(port: int, host: str, transport: str, log_level: str) -> None:
    """Launch the AgeMCP server with the specified configuration.

    Override any settings from the .env file using standardized pydantic-settings syntax of
    
    <model>__<field>=<value> => MCP__PORT=7999
    
    Note: see all settings using the `settings` command.

    """
    cmd = "fastmcp"
    spec = SETTINGS.app.package_path / "server.py"
    full_cmd = [str(cmd), "run", str(spec), "--port", str(port), "--host", host, "--transport", transport, "--log-level", log_level]
    
    console.log(f"Running server with command: {' '.join(full_cmd)}")

    os.chdir(str(SETTINGS.app.root_path))
    os.execvp(str(cmd), full_cmd)
    


def main() -> None:
    """
    Main entry point for the CLI application.

    Invokes the CLI group, enabling command-line interaction.
    """
    cli()
