"""Tests for cpr.player.human (HumanPlayer)."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from cpr.player.human import HumanPlayer


@pytest.fixture()
def player() -> HumanPlayer:
    return HumanPlayer()


@pytest.fixture()
def mock_game() -> MagicMock:
    game = MagicMock()
    game.output_fd = 12
    game.input_fd = 11
    game.is_running.return_value = False
    return game


class TestPlay:
    @patch("cpr.player.human.termios.tcsetattr")
    @patch("cpr.player.human.tty.setraw")
    @patch("cpr.player.human.termios.tcgetattr", return_value=[1, 2, 3])
    def test_puts_terminal_in_raw_mode_and_restores(
        self,
        mock_tcgetattr: MagicMock,
        mock_setraw: MagicMock,
        mock_tcsetattr: MagicMock,
        player: HumanPlayer,
        mock_game: MagicMock,
    ) -> None:
        stdin = MagicMock()
        stdin.fileno.return_value = 0

        player.play(mock_game, stdin=stdin)

        mock_tcgetattr.assert_called_once_with(0)
        mock_setraw.assert_called_once_with(0)
        mock_tcsetattr.assert_called_once()

    @patch("cpr.player.human.termios.tcsetattr")
    @patch("cpr.player.human.tty.setraw")
    @patch("cpr.player.human.termios.tcgetattr", return_value=[1, 2, 3])
    def test_restores_terminal_on_exception(
        self,
        mock_tcgetattr: MagicMock,
        mock_setraw: MagicMock,
        mock_tcsetattr: MagicMock,
        player: HumanPlayer,
        mock_game: MagicMock,
    ) -> None:
        stdin = MagicMock()
        stdin.fileno.return_value = 0
        mock_game.is_running.side_effect = RuntimeError("boom")

        with pytest.raises(RuntimeError, match="boom"):
            player.play(mock_game, stdin=stdin)

        mock_tcsetattr.assert_called_once()


class TestIOLoop:
    @patch("cpr.player.human.os.write")
    @patch("cpr.player.human.os.read")
    @patch("cpr.player.human.select.select")
    def test_relays_game_output_to_stdout_and_feeds_parser(
        self,
        mock_select: MagicMock,
        mock_read: MagicMock,
        mock_write: MagicMock,
        player: HumanPlayer,
        mock_game: MagicMock,
    ) -> None:
        mock_game.is_running.side_effect = [True, False]
        mock_select.return_value = ([mock_game.output_fd], [], [])
        mock_read.return_value = b"\x1b[11;41H@"

        HumanPlayer._io_loop(mock_game, fd_in=0)

        mock_read.assert_called_with(mock_game.output_fd, 4096)
        mock_game.feed.assert_called_once_with(b"\x1b[11;41H@")
        mock_write.assert_called_with(sys.stdout.fileno(), b"\x1b[11;41H@")

    @patch("cpr.player.human.os.write")
    @patch("cpr.player.human.os.read")
    @patch("cpr.player.human.select.select")
    def test_relays_stdin_to_game_input(
        self,
        mock_select: MagicMock,
        mock_read: MagicMock,
        mock_write: MagicMock,
        player: HumanPlayer,
        mock_game: MagicMock,
    ) -> None:
        fd_in = 0
        mock_game.is_running.side_effect = [True, False]
        mock_select.return_value = ([fd_in], [], [])
        mock_read.return_value = b"h"

        HumanPlayer._io_loop(mock_game, fd_in=fd_in)

        mock_read.assert_called_with(fd_in, 1024)
        mock_write.assert_called_with(mock_game.input_fd, b"h")

    @patch("cpr.player.human.os.write")
    @patch("cpr.player.human.os.read")
    @patch("cpr.player.human.select.select")
    def test_stops_on_eof_from_game(
        self,
        mock_select: MagicMock,
        mock_read: MagicMock,
        mock_write: MagicMock,
        player: HumanPlayer,
        mock_game: MagicMock,
    ) -> None:
        mock_game.is_running.return_value = True
        mock_select.return_value = ([mock_game.output_fd], [], [])
        mock_read.return_value = b""

        HumanPlayer._io_loop(mock_game, fd_in=0)

        mock_game.feed.assert_not_called()

    @patch("cpr.player.human.os.write")
    @patch("cpr.player.human.os.read")
    @patch("cpr.player.human.select.select")
    def test_handles_keyboard_interrupt(
        self,
        mock_select: MagicMock,
        mock_read: MagicMock,
        mock_write: MagicMock,
        player: HumanPlayer,
        mock_game: MagicMock,
    ) -> None:
        mock_game.is_running.return_value = True
        mock_select.side_effect = KeyboardInterrupt

        HumanPlayer._io_loop(mock_game, fd_in=0)
