"""Tag operation tests.

Arrange markdown → parse → mutate tags → write → assert output markdown.
"""

from obsidian_kanban_parser import parse, write
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
    assert list(item.tags) == ["#bug", "#frontend"]


def test_tags_len() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task #bug #frontend")))
    board = parse(md)

    # act
    item = get_lane(board, "Todo").items[0]

    # assert
    assert len(item.tags) == 2


def test_tags_contains_with_hash() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task #bug")))
    board = parse(md)

    # act
    item = get_lane(board, "Todo").items[0]

    # assert
    assert "#bug" in item.tags


def test_tags_contains_without_hash() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task #bug")))
    board = parse(md)

    # act
    item = get_lane(board, "Todo").items[0]

    # assert
    assert "bug" in item.tags


def test_tags_not_contains() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task #bug")))
    board = parse(md)

    # act
    item = get_lane(board, "Todo").items[0]

    # assert
    assert "#frontend" not in item.tags


# ---------------------------------------------------------------------------
# tags.add
# ---------------------------------------------------------------------------


def test_add_tag_to_item() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    item.tags.add("#urgent")
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
    item.tags.add("#urgent")
    result_md = write(board)

    # assert — markdown unchanged
    assert_markdown_is_equal(result_md, md)


def test_add_tag_without_hash_normalizes() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    item.tags.add("urgent")
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Task #urgent")))
    assert_markdown_is_equal(result_md, expected_md)


# ---------------------------------------------------------------------------
# tags.remove / tags.discard
# ---------------------------------------------------------------------------


def test_remove_tag_from_item() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task #bug #frontend")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    item.tags.remove("#bug")
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
    item.tags.remove("#nonexistent")
    result_md = write(board)

    # assert — markdown unchanged
    assert_markdown_is_equal(result_md, md)


def test_remove_one_of_multiple_tags() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task #bug #frontend #urgent")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    item.tags.remove("#frontend")
    result_md = write(board)

    # assert — only #frontend removed, others preserved
    expected_md = make_board(make_lane("Todo", make_item("Task #bug #urgent")))
    assert_markdown_is_equal(result_md, expected_md)


def test_discard_is_alias_for_remove() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task #bug")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    item.tags.remove("#bug")
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Task")))
    assert_markdown_is_equal(result_md, expected_md)
