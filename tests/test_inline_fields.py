"""Inline field operation tests.

Arrange markdown → parse → read/mutate inline fields → write → assert.
"""

import datetime

from obsidian_kanban_parser import parse, write
from tests.helpers import assert_markdown_is_equal, get_lane, make_board, make_item, make_lane

# ---------------------------------------------------------------------------
# Group 1: Reading (type coercion)
# ---------------------------------------------------------------------------


def test_read_inline_field_returns_string() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task [priority::high]")))
    board = parse(md)

    # act
    item = get_lane(board, "Todo").items[0]
    result = item.inline_fields["priority"]

    # assert
    assert result == "high"
    assert isinstance(result, str)


def test_read_inline_field_returns_date() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task [due::2024-06-01]")))
    board = parse(md)

    # act
    item = get_lane(board, "Todo").items[0]
    result = item.inline_fields["due"]

    # assert
    assert result == datetime.date(2024, 6, 1)
    assert isinstance(result, datetime.date)


def test_read_inline_field_returns_int() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task [count::42]")))
    board = parse(md)

    # act
    item = get_lane(board, "Todo").items[0]
    result = item.inline_fields["count"]

    # assert
    assert result == 42
    assert isinstance(result, int)


def test_read_inline_field_returns_float() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task [cost::4.5]")))
    board = parse(md)

    # act
    item = get_lane(board, "Todo").items[0]
    result = item.inline_fields["cost"]

    # assert
    assert result == 4.5
    assert isinstance(result, float)


def test_read_missing_inline_field_returns_none() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")))
    board = parse(md)

    # act
    item = get_lane(board, "Todo").items[0]
    result = item.inline_fields["due"]

    # assert
    assert result is None


def test_read_paren_style_inline_field() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task (due::2024-06-01)")))
    board = parse(md)

    # act
    item = get_lane(board, "Todo").items[0]
    result = item.inline_fields["due"]

    # assert
    assert result == datetime.date(2024, 6, 1)


# ---------------------------------------------------------------------------
# Group 2: Writing (serialization)
# ---------------------------------------------------------------------------


def test_set_inline_field_string() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    item.inline_fields["priority"] = "high"
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Task [priority::high]")))
    assert_markdown_is_equal(result_md, expected_md)


def test_set_inline_field_date() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    item.inline_fields["scheduled"] = datetime.date(2024, 6, 1)
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Task [scheduled::2024-06-01]")))
    assert_markdown_is_equal(result_md, expected_md)


def test_set_inline_field_int() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    item.inline_fields["count"] = 42
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Task [count::42]")))
    assert_markdown_is_equal(result_md, expected_md)


def test_set_inline_field_float() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    item.inline_fields["cost"] = 4.5
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Task [cost::4.5]")))
    assert_markdown_is_equal(result_md, expected_md)


def test_set_two_inline_fields() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    item.inline_fields["priority"] = "high"
    item.inline_fields["due"] = datetime.date(2024, 6, 1)
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Task [priority::high] [due::2024-06-01]")))
    assert_markdown_is_equal(result_md, expected_md)


def test_update_existing_inline_field() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task [priority::low]")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    item.inline_fields["priority"] = "high"
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Task [priority::high]")))
    assert_markdown_is_equal(result_md, expected_md)


# ---------------------------------------------------------------------------
# Group 3: Delete
# ---------------------------------------------------------------------------


def test_delete_inline_field() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task [priority::high]")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    del item.inline_fields["priority"]
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Task")))
    assert_markdown_is_equal(result_md, expected_md)


def test_delete_inline_field_preserves_others() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task [priority::high] [due::2024-06-01]")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]

    # act
    del item.inline_fields["priority"]
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Task [due::2024-06-01]")))
    assert_markdown_is_equal(result_md, expected_md)


def test_delete_missing_field_is_noop() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]
    original_title_raw = item.title_raw

    # act
    del item.inline_fields["nonexistent"]

    # assert
    assert item.title_raw == original_title_raw


# ---------------------------------------------------------------------------
# Group 4: Contains
# ---------------------------------------------------------------------------


def test_contains_true() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task [due::2024-06-01]")))
    board = parse(md)

    # act / assert
    item = get_lane(board, "Todo").items[0]
    assert "due" in item.inline_fields


def test_contains_false() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task")))
    board = parse(md)

    # act / assert
    item = get_lane(board, "Todo").items[0]
    assert "due" not in item.inline_fields


# ---------------------------------------------------------------------------
# Group 5: Integration with search
# ---------------------------------------------------------------------------


def test_find_by_inline_field_after_set() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task A"), make_item("Task B")))
    board = parse(md)
    item_a = get_lane(board, "Todo").items[0]

    # act
    item_a.inline_fields["owner"] = "alice"
    results = board.find_items_by_inline_field("owner", "alice")

    # assert
    assert len(results) == 1
    _, found = results[0]
    assert found is item_a


# ---------------------------------------------------------------------------
# Group 6: Edge cases
# ---------------------------------------------------------------------------


def test_value_that_looks_like_date_but_isnt_stays_string() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task [ref::2024-13-01]")))
    board = parse(md)

    # act
    item = get_lane(board, "Todo").items[0]
    result = item.inline_fields["ref"]

    # assert — invalid month, stays as string
    assert result == "2024-13-01"
    assert isinstance(result, str)


def test_value_that_looks_like_number_but_isnt_stays_string() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task [version::1.2.3]")))
    board = parse(md)

    # act
    item = get_lane(board, "Todo").items[0]
    result = item.inline_fields["version"]

    # assert
    assert result == "1.2.3"
    assert isinstance(result, str)


def test_negative_int() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task [offset::-5]")))
    board = parse(md)

    # act
    item = get_lane(board, "Todo").items[0]
    result = item.inline_fields["offset"]

    # assert
    assert result == -5
    assert isinstance(result, int)
