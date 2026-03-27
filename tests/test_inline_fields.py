"""Inline field operation tests.

Arrange markdown → parse → read/mutate inline fields → write → assert.
"""

from obsidian_kanban_parser import find_items_by_inline_field, find_lane_by_name, parse, write

from tests.helpers import assert_markdown_is_equal, make_board, make_item, make_lane


# ---------------------------------------------------------------------------
# Reading inline fields
# ---------------------------------------------------------------------------


def test_read_inline_field_value() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task [due::2024-06-01]")))
    board = parse(md)

    # act
    lane = find_lane_by_name(board, "Todo")
    assert lane is not None
    item = lane.items[0]

    # assert
    assert item.inline_field("due") == "2024-06-01"


def test_read_missing_inline_field_returns_none() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")))
    board = parse(md)

    # act
    lane = find_lane_by_name(board, "Todo")
    assert lane is not None
    item = lane.items[0]

    # assert
    assert item.inline_field("due") is None


# ---------------------------------------------------------------------------
# set_inline_field — add
# ---------------------------------------------------------------------------


def test_add_inline_field() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")))
    board = parse(md)
    lane = find_lane_by_name(board, "Todo")
    assert lane is not None
    item = lane.items[0]

    # act
    item.set_inline_field("priority", "high")
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Task [priority::high]")))
    assert_markdown_is_equal(result_md, expected_md)


def test_add_two_inline_fields() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")))
    board = parse(md)
    lane = find_lane_by_name(board, "Todo")
    assert lane is not None
    item = lane.items[0]

    # act
    item.set_inline_field("priority", "high")
    item.set_inline_field("due", "2024-06-01")
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Task [priority::high] [due::2024-06-01]")))
    assert_markdown_is_equal(result_md, expected_md)


# ---------------------------------------------------------------------------
# set_inline_field — update existing
# ---------------------------------------------------------------------------


def test_update_existing_inline_field() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task [priority::low]")))
    board = parse(md)
    lane = find_lane_by_name(board, "Todo")
    assert lane is not None
    item = lane.items[0]

    # act
    item.set_inline_field("priority", "high")
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Task [priority::high]")))
    assert_markdown_is_equal(result_md, expected_md)


# ---------------------------------------------------------------------------
# Combining with search
# ---------------------------------------------------------------------------


def test_find_by_inline_field_after_set() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task A"), make_item("Task B")))
    board = parse(md)
    lane = find_lane_by_name(board, "Todo")
    assert lane is not None
    item_a = lane.items[0]

    # act — set field on item A only
    item_a.set_inline_field("owner", "alice")
    results = find_items_by_inline_field(board, "owner", "alice")

    # assert — only item A is returned
    assert len(results) == 1
    _, found = results[0]
    assert found is item_a
