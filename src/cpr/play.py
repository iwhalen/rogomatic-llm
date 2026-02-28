"""Start and orchestrate a game of Rogue."""

import os

from cpr.config import CPRSettings, PlayerType
from cpr.external.game import RogueGame
from cpr.player.human import HumanPlayer


def play(config: CPRSettings) -> None:
    """Play a game of Rogue given the config."""
    rogue_path = config.rogue_path.resolve()

    if not rogue_path.exists():
        raise FileNotFoundError(
            f"Rogue executable not found at {rogue_path}. "
            "Run 'make build' first to compile the rogue binary."
        )

    match config.player:
        case PlayerType.HUMAN:
            _play_human(config)
        case PlayerType.CLAUDE:
            raise NotImplementedError("Claude player is not yet implemented")


def _play_human(config: CPRSettings) -> None:
    """Launch an interactive human-played Rogue session."""
    rogue_path = config.rogue_path.resolve()
    rogue_dir = str(rogue_path.parent)
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = rogue_dir

    original_cwd = os.getcwd()
    os.chdir(rogue_dir)
    try:
        with RogueGame(
            rogue_executable=str(rogue_path),
            args=[config.rogue_version],
            env=env,
        ) as game:
            player = HumanPlayer()
            player.play(game)
    finally:
        os.chdir(original_cwd)
