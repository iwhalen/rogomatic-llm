"""Abstract base class for Rogue players."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cpr.external.game import RogueGame


class Player(ABC):
    """Contract for a player that interacts with a running Rogue game."""

    @abstractmethod
    def play(self, game: RogueGame) -> None:
        """Take control and play the game until it ends or the player quits."""
