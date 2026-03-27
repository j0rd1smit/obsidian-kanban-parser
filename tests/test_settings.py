"""Settings block tests.

Reading is tested directly on parsed board objects.
Mutation tests clear _settings_raw so the writer regenerates JSON from the
mutated dict (round-trip via write → parse).
"""

from obsidian_kanban_parser import parse, write
from tests.helpers import make_board, make_lane

# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------


def test_read_settings_value() -> None:
    # arrange
    md = make_board(make_lane("Todo"), settings={"kanban-plugin": "board", "my-setting": True})
    board = parse(md)

    # assert
    assert board.settings is not None
    assert board.settings["my-setting"] is True


def test_board_with_no_settings_block_has_none() -> None:
    # arrange
    md = make_board(make_lane("Todo"))
    board = parse(md)

    # assert
    assert board.settings is None


# ---------------------------------------------------------------------------
# Mutation + write-back
# (_settings_raw is cleared to force the writer to regenerate JSON from the dict)
# ---------------------------------------------------------------------------


def test_update_settings_value() -> None:
    # arrange
    md = make_board(make_lane("Todo"), settings={"kanban-plugin": "board"})
    board = parse(md)

    # act
    assert board.settings is not None
    board.settings["new-key"] = "new-value"
    board._settings_raw = None
    result_board = parse(write(board))

    # assert
    assert result_board.settings is not None
    assert result_board.settings["new-key"] == "new-value"
