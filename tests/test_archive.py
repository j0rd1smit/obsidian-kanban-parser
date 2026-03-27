"""Archive operation tests.

Arrange markdown → parse → archive/unarchive → write → assert via helpers.
"""

from obsidian_kanban_parser import archive_item, find_lane_by_name, parse, unarchive_item, write

from tests.helpers import (
    assert_item_in_archive,
    assert_item_in_lane,
    assert_item_not_in_archive,
    assert_item_not_in_lane,
    assert_markdown_is_equal,
    make_board,
    make_item,
    make_lane,
)


# ---------------------------------------------------------------------------
# archive_item
# ---------------------------------------------------------------------------


def test_archive_item_removes_it_from_lane() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")))
    board = parse(md)
    lane = find_lane_by_name(board, "Todo")
    assert lane is not None
    item = lane.items[0]

    # act
    archive_item(board, item, "Todo")
    result_board = parse(write(board))

    # assert
    result_lane = find_lane_by_name(result_board, "Todo")
    assert result_lane is not None
    assert_item_not_in_lane(result_lane, "Task")


def test_archive_item_appears_in_archive_section() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")))
    board = parse(md)
    lane = find_lane_by_name(board, "Todo")
    assert lane is not None
    item = lane.items[0]

    # act
    archive_item(board, item, "Todo")
    result_board = parse(write(board))

    # assert
    assert_item_in_archive(result_board, "Task")


def test_archive_item_write_matches_expected_markdown() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")))
    board = parse(md)
    lane = find_lane_by_name(board, "Todo")
    assert lane is not None
    item = lane.items[0]

    # act
    archive_item(board, item, "Todo")
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo"), archive=[make_item("Task")])
    assert_markdown_is_equal(result_md, expected_md)


# ---------------------------------------------------------------------------
# unarchive_item
# ---------------------------------------------------------------------------


def test_unarchive_item_appears_in_target_lane() -> None:
    # arrange
    md = make_board(make_lane("Todo"), archive=[make_item("Old task", checked=True)])
    board = parse(md)
    item = board.archive[0]

    # act
    unarchive_item(board, item, "Todo")
    result_board = parse(write(board))

    # assert
    result_lane = find_lane_by_name(result_board, "Todo")
    assert result_lane is not None
    assert_item_in_lane(result_lane, "Old task")


def test_unarchive_item_removed_from_archive() -> None:
    # arrange
    md = make_board(make_lane("Todo"), archive=[make_item("Old task", checked=True)])
    board = parse(md)
    item = board.archive[0]

    # act
    unarchive_item(board, item, "Todo")
    result_board = parse(write(board))

    # assert
    assert_item_not_in_archive(result_board, "Old task")
