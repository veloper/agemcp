import os

import click

from rich.console import Console
from rich.traceback import install as install_traceback


console = Console()
install_traceback(show_locals=True, word_wrap=True, console=console)


class Context:
    def __init__(self):
        pass

    def settings(self):
        """Return the settings for the current context."""
        from agemcp.settings import get_settings
        return get_settings()
    
        


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """AgeMCP: Apache Age Model Context Protocol Server CLI."""
    ctx.obj = Context()


#  fastmcp run ./src/mymcp/server.py --port 7999 --host 0.0.0.0 --transport streamable-http --log-level=DEBUG

@cli.command()
@click.option('--port', default=7999, help='Port to run the server on.')
@click.option('--host', default='0.0.0.0', help='Host to run the server on.')
@click.option('--transport', type=click.Choice(['sse', 'streamable-http', 'stdio']), help='Transport to use.', default='streamable-http')
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']), default='DEBUG', help='Log level to use.')
@click.pass_obj
def run(ctx: Context, port: int, host: str, transport: str, log_level: str) -> None:
    """
    Run the AgeMCP server.
    """
    cmd = "fastmcp"
    spec = ctx.settings().app.package_path / "server.py"
    full_cmd = [str(cmd), "run", str(spec), "--port", str(port), "--host", host, "--transport", transport, "--log-level", log_level]
    
    console.log(f"Running server with command: {' '.join(full_cmd)}")
    
    os.chdir(str(ctx.settings().app.root_path))
    os.execvp(str(cmd), full_cmd)
    


def main() -> None:
    cli()
