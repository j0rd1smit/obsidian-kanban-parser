"""Frontmatter and settings tests.

Reading is tested directly on parsed board objects.
Writing mutations requires clearing the preserved raw strings so the writer
regenerates them from the mutated dicts.
"""

from obsidian_kanban_parser import parse, write

from tests.helpers import make_board, make_lane


# ---------------------------------------------------------------------------
# Frontmatter — reading
# ---------------------------------------------------------------------------


def test_read_frontmatter_field() -> None:
    # arrange — custom frontmatter with a known field
    frontmatter = "---\n\nkanban-plugin: board\ncustom-field: my-value\n\n---\n"
    md = make_board(make_lane("Todo"), frontmatter=frontmatter)
    board = parse(md)

    # assert
    assert board.frontmatter["custom-field"] == "my-value"


def test_board_with_no_frontmatter_has_empty_dict() -> None:
    # arrange — no frontmatter section at all
    md = make_board(make_lane("Todo"), frontmatter="")
    board = parse(md)

    # assert
    assert board.frontmatter == {}


# ---------------------------------------------------------------------------
# Frontmatter — mutation + write-back
#
# _frontmatter_raw is cleared so the writer regenerates from the mutated dict.
# ---------------------------------------------------------------------------


def test_update_frontmatter_field() -> None:
    # arrange
    frontmatter = "---\n\nkanban-plugin: board\n\n---\n"
    md = make_board(make_lane("Todo"), frontmatter=frontmatter)
    board = parse(md)

    # act
    board.frontmatter["custom-field"] = "new-value"
    board._frontmatter_raw = ""  # force writer to regenerate from dict
    result_board = parse(write(board))

    # assert
    assert result_board.frontmatter["custom-field"] == "new-value"


def test_add_new_frontmatter_field() -> None:
    # arrange
    md = make_board(make_lane("Todo"))
    board = parse(md)

    # act
    board.frontmatter["new-field"] = "hello"
    board._frontmatter_raw = ""
    result_board = parse(write(board))

    # assert
    assert result_board.frontmatter["new-field"] == "hello"


def test_remove_frontmatter_field() -> None:
    # arrange
    frontmatter = "---\n\nkanban-plugin: board\nto-remove: gone\n\n---\n"
    md = make_board(make_lane("Todo"), frontmatter=frontmatter)
    board = parse(md)

    # act
    del board.frontmatter["to-remove"]
    board._frontmatter_raw = ""
    result_board = parse(write(board))

    # assert
    assert "to-remove" not in result_board.frontmatter


# ---------------------------------------------------------------------------
# Settings — reading
# ---------------------------------------------------------------------------


def test_read_settings_value() -> None:
    # arrange
    md = make_board(make_lane("Todo"), settings={"kanban-plugin": "board", "my-setting": True})
    board = parse(md)

    # assert
    assert board.settings is not None
    assert board.settings["my-setting"] is True


def test_board_with_no_settings_block_has_none() -> None:
    # arrange — no settings block
    md = make_board(make_lane("Todo"))
    board = parse(md)

    # assert
    assert board.settings is None


# ---------------------------------------------------------------------------
# Settings — mutation + write-back
#
# _settings_raw is cleared so the writer regenerates JSON from the mutated dict.
# ---------------------------------------------------------------------------


def test_update_settings_value() -> None:
    # arrange
    md = make_board(make_lane("Todo"), settings={"kanban-plugin": "board"})
    board = parse(md)

    # act
    assert board.settings is not None
    board.settings["new-key"] = "new-value"
    board._settings_raw = None  # force writer to regenerate from dict
    result_board = parse(write(board))

    # assert
    assert result_board.settings is not None
    assert result_board.settings["new-key"] == "new-value"
