"""Frontmatter tests.

Reading is tested directly on parsed board objects.
Mutation tests clear _frontmatter_raw so the writer regenerates from the
mutated dict (round-trip via write → parse).
"""

from obsidian_kanban_parser import parse, write
from tests.helpers import make_board, make_frontmatter, make_lane

# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------


def test_read_frontmatter_field() -> None:
    # arrange
    md = make_board(make_lane("Todo"), frontmatter=make_frontmatter({"custom-field": "my-value"}))
    board = parse(md)

    # assert
    assert board.frontmatter["custom-field"] == "my-value"


def test_board_with_no_frontmatter_has_empty_dict() -> None:
    # arrange
    md = make_board(make_lane("Todo"), frontmatter="")
    board = parse(md)

    # assert
    assert board.frontmatter == {}


# ---------------------------------------------------------------------------
# Mutation + write-back
# (_frontmatter_raw is cleared to force the writer to regenerate from the dict)
# ---------------------------------------------------------------------------


def test_update_frontmatter_field() -> None:
    # arrange
    md = make_board(make_lane("Todo"), frontmatter=make_frontmatter())
    board = parse(md)

    # act
    board.frontmatter["custom-field"] = "new-value"
    board._frontmatter_raw = ""
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
    md = make_board(make_lane("Todo"), frontmatter=make_frontmatter({"to-remove": "gone"}))
    board = parse(md)

    # act
    del board.frontmatter["to-remove"]
    board._frontmatter_raw = ""
    result_board = parse(write(board))

    # assert
    assert "to-remove" not in result_board.frontmatter
