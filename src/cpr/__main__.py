from pathlib import Path
from typing import Annotated

import typer

from cpr.config import (
    DEFAULT_ROGUE_PATH,
    DEFAULT_ROGUE_VERSION,
    CPRSettings,
    PlayerType,
    RogueVersion,
)
from cpr.play import play

_BY = "\033[1;33m"
_R = "\033[0m"

BANNER = (
    f"\n{_BY}\u00b7  \u00b7  \u00b7  Claude Plays Rogue  \u00b7  \u00b7  \u00b7{_R}\n\n"
)

app = typer.Typer()


@app.command()
def main(
    player: Annotated[
        PlayerType,
        typer.Option(
            help="Type of player: 'human' or 'claude'.",
            case_sensitive=False,
        ),
    ] = PlayerType.CLAUDE,
    rogue_path: Annotated[
        Path,
        typer.Option(
            help="Path to the rogue executable.",
        ),
    ] = DEFAULT_ROGUE_PATH,
    rogue_version: Annotated[
        RogueVersion,
        typer.Option(
            help="Rogue version to play.",
            case_sensitive=False,
        ),
    ] = DEFAULT_ROGUE_VERSION,
) -> None:
    """Main typer application. Starts the play session with the given options."""
    typer.echo(BANNER)
    settings = CPRSettings(
        player=player,
        rogue_path=rogue_path,
        rogue_version=rogue_version,
    )
    play(settings)


def cli() -> None:
    app()


if __name__ == "__main__":
    cli()
