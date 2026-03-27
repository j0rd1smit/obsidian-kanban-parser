"""Tag operation tests.

Arrange markdown → parse → mutate tags → write → assert output markdown.
"""

from obsidian_kanban_parser import find_items_by_tag, parse, write
from tests.helpers import assert_markdown_is_equal, get_lane, make_board, make_item, make_lane

# ---------------------------------------------------------------------------
# Reading tags
# ---------------------------------------------------------------------------


def test_read_tags_from_item() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task #bug #frontend")))
    board = parse(md)

    # act
    item = get_lane(board, "Todo").items[0]

    # assert
    assert item.tags == ["#bug", "#frontend"]


# ---------------------------------------------------------------------------
# add_tag
# ---------------------------------------------------------------------------


def test_add_tag_to_item() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    item.add_tag("#urgent")
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Task #urgent")))
    assert_markdown_is_equal(result_md, expected_md)


def test_add_tag_is_idempotent() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task #urgent")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act — add tag that already exists
    item.add_tag("#urgent")
    result_md = write(board)

    # assert — markdown unchanged
    assert_markdown_is_equal(result_md, md)


# ---------------------------------------------------------------------------
# remove_tag
# ---------------------------------------------------------------------------


def test_remove_tag_from_item() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task #bug #frontend")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    item.remove_tag("#bug")
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Task #frontend")))
    assert_markdown_is_equal(result_md, expected_md)


def test_remove_tag_not_present_is_safe() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task #bug")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act — remove tag that does not exist
    item.remove_tag("#nonexistent")
    result_md = write(board)

    # assert — markdown unchanged
    assert_markdown_is_equal(result_md, md)


def test_remove_one_of_multiple_tags() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task #bug #frontend #urgent")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    item.remove_tag("#frontend")
    result_md = write(board)

    # assert — only #frontend removed, others preserved
    expected_md = make_board(make_lane("Todo", make_item("Task #bug #urgent")))
    assert_markdown_is_equal(result_md, expected_md)


# ---------------------------------------------------------------------------
# Case sensitivity
# ---------------------------------------------------------------------------


def test_tag_search_is_case_sensitive() -> None:
    # arrange — item has #Bug (capital B)
    md = make_board(make_lane("Todo", make_item("Task #Bug")))
    board = parse(md)

    # act
    results_exact = find_items_by_tag(board, "#Bug")
    results_lower = find_items_by_tag(board, "#bug")

    # assert — only the exact case matches
    assert len(results_exact) == 1
    assert len(results_lower) == 0
