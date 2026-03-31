"""Task lifecycle tests: add, remove, move items, and checked setter.

Arrange markdown → parse → mutate → write → assert output markdown.
"""

from obsidian_kanban_parser import move_item, parse, write
from tests.helpers import assert_markdown_is_equal, get_lane, make_board, make_item, make_lane

# ---------------------------------------------------------------------------
# lane.add_item
# ---------------------------------------------------------------------------


def test_add_item_to_lane_appended_at_end() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Existing")))
    board = parse(md)

    # act
    get_lane(board, "Todo").add_item("New task")
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Existing"), make_item("New task")))
    assert_markdown_is_equal(result_md, expected_md)


def test_add_item_at_position_zero() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Existing")))
    board = parse(md)

    # act
    get_lane(board, "Todo").add_item("New task", position=0)
    result_md = write(board)

    # assert — new item is first
    expected_md = make_board(make_lane("Todo", make_item("New task"), make_item("Existing")))
    assert_markdown_is_equal(result_md, expected_md)


def test_add_checked_item() -> None:
    # arrange
    md = make_board(make_lane("Done"))
    board = parse(md)

    # act
    get_lane(board, "Done").add_item("Finished task", check_char="x")
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Done", make_item("Finished task", checked=True)))
    assert_markdown_is_equal(result_md, expected_md)


# ---------------------------------------------------------------------------
# lane.remove_item
# ---------------------------------------------------------------------------


def test_remove_item_from_lane() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Keep"), make_item("Remove me")))
    board = parse(md)
    item = get_lane(board, "Todo").items[1]  # "Remove me"

    # act
    result = get_lane(board, "Todo").remove_item(item)
    result_md = write(board)

    # assert
    assert result is True
    expected_md = make_board(make_lane("Todo", make_item("Keep")))
    assert_markdown_is_equal(result_md, expected_md)


def test_remove_item_not_in_lane_returns_false() -> None:
    # arrange — item is in "Todo" but we try to remove from "Done"
    md = make_board(make_lane("Todo", make_item("Task")), make_lane("Done"))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    result = get_lane(board, "Done").remove_item(item)

    # assert
    assert result is False


# ---------------------------------------------------------------------------
# move_item
# ---------------------------------------------------------------------------


def test_move_item_to_another_lane() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")), make_lane("Done"))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    move_item(item, from_lane=get_lane(board, "Todo"), to_lane=get_lane(board, "Done"))
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo"), make_lane("Done", make_item("Task")))
    assert_markdown_is_equal(result_md, expected_md)


def test_move_item_to_position_zero_in_destination() -> None:
    # arrange
    md = make_board(
        make_lane("Todo", make_item("Moving")),
        make_lane("Done", make_item("Existing")),
    )
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    move_item(item, from_lane=get_lane(board, "Todo"), to_lane=get_lane(board, "Done"), position=0)
    result_md = write(board)

    # assert — "Moving" is inserted before "Existing"
    expected_md = make_board(
        make_lane("Todo"),
        make_lane("Done", make_item("Moving"), make_item("Existing")),
    )
    assert_markdown_is_equal(result_md, expected_md)


# ---------------------------------------------------------------------------
# checked setter
# ---------------------------------------------------------------------------


def test_set_checked_true() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    item.checked = True
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Task", checked=True)))
    assert_markdown_is_equal(result_md, expected_md)


def test_set_checked_false() -> None:
    # arrange
    md = make_board(make_lane("Done", make_item("Task", checked=True)))
    board = parse(md)
    item = get_lane(board, "Done").items[0]

    # act
    item.checked = False
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Done", make_item("Task")))
    assert_markdown_is_equal(result_md, expected_md)
