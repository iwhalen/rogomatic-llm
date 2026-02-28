"""Human player that relays terminal I/O to and from a Rogue game."""

from __future__ import annotations

import os
import select
import sys
import termios
import tty
from typing import TYPE_CHECKING, Any

from cpr.player.base import Player

if TYPE_CHECKING:
    from cpr.external.game import RogueGame

_SAVE_CUR = b"\0337"
_RESTORE_CUR = b"\0338"
_PROMPT_POS = b"\033[26;1H"
_CLEAR_LINE = b"\033[2K"
_PROMPT_TEXT = b"> "

_SHOW_PROMPT = _SAVE_CUR + _PROMPT_POS + _CLEAR_LINE + _PROMPT_TEXT + _RESTORE_CUR
_HIDE_PROMPT = _SAVE_CUR + _PROMPT_POS + _CLEAR_LINE + _RESTORE_CUR

_ESC = 0x1B

_ANSI_TO_ROGUE: dict[bytes, bytes] = {
    b"\x1b[A": b"k",       # Up
    b"\x1b[B": b"j",       # Down
    b"\x1b[C": b"l",       # Right
    b"\x1b[D": b"h",       # Left
    b"\x1bOA": b"k",       # Up    (application mode)
    b"\x1bOB": b"j",       # Down  (application mode)
    b"\x1bOC": b"l",       # Right (application mode)
    b"\x1bOD": b"h",       # Left  (application mode)
    b"\x1b[H": b"y",       # Home  (xterm)
    b"\x1b[F": b"b",       # End   (xterm)
    b"\x1bOH": b"y",       # Home  (application mode)
    b"\x1bOF": b"b",       # End   (application mode)
    b"\x1b[1~": b"y",      # Home  (vt220)
    b"\x1b[4~": b"b",      # End   (vt220)
    b"\x1b[5~": b"u",      # Page Up
    b"\x1b[6~": b"n",      # Page Down
}

_MAX_SEQ_LEN = max(len(s) for s in _ANSI_TO_ROGUE)


def _translate_keys(data: bytes) -> bytes:
    """Replace ANSI arrow/nav escape sequences with rogue vi-keys."""
    out = bytearray()
    i = 0
    n = len(data)
    while i < n:
        if data[i] == _ESC and i + 1 < n:
            matched = False
            for length in range(min(_MAX_SEQ_LEN, n - i), 1, -1):
                seq = data[i : i + length]
                replacement = _ANSI_TO_ROGUE.get(seq)
                if replacement is not None:
                    out.extend(replacement)
                    i += length
                    matched = True
                    break
            if not matched:
                out.append(data[i])
                i += 1
        else:
            out.append(data[i])
            i += 1
    return bytes(out)


class HumanPlayer(Player):
    """Interactive terminal player.

    Puts the terminal in raw mode and relays keystrokes to the game
    while displaying the game's VT100 output on stdout.  The game's
    internal :class:`ScreenState` is kept in sync via
    :meth:`RogueGame.feed`.
    """

    def play(self, game: RogueGame, stdin: Any = None) -> None:
        """Run an interactive loop forwarding terminal I/O.

        Press Ctrl-C to quit.
        """
        fd_in = (stdin or sys.stdin).fileno()
        old_settings = termios.tcgetattr(fd_in)
        try:
            tty.setraw(fd_in)
            self._io_loop(game, fd_in)
        finally:
            termios.tcsetattr(fd_in, termios.TCSADRAIN, old_settings)

    @staticmethod
    def _io_loop(game: RogueGame, fd_in: int) -> None:
        """Bidirectional relay between the human's terminal and Rogue."""
        frogue = game.output_fd
        trogue = game.input_fd
        stdout = sys.stdout.fileno()
        prompt_visible = False
        try:
            while game.is_running():
                rlist, _, _ = select.select([frogue, fd_in], [], [], 0.1)
                if not rlist:
                    if not prompt_visible:
                        os.write(stdout, _SHOW_PROMPT)
                        prompt_visible = True
                    continue
                if frogue in rlist:
                    if prompt_visible:
                        os.write(stdout, _HIDE_PROMPT)
                        prompt_visible = False
                    try:
                        data = os.read(frogue, 4096)
                    except OSError:
                        break
                    if not data:
                        break
                    game.feed(data)
                    os.write(stdout, data)
                if fd_in in rlist:
                    if prompt_visible:
                        os.write(stdout, _HIDE_PROMPT)
                        prompt_visible = False
                    data = os.read(fd_in, 1024)
                    if not data:
                        break
                    os.write(trogue, _translate_keys(data))
        except KeyboardInterrupt:
            pass
        finally:
            if prompt_visible:
                os.write(stdout, _HIDE_PROMPT)
