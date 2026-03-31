"""Search / read tests.

Each test arranges a known markdown input, calls a read/query API,
and asserts on the returned domain objects (not on raw markdown).
"""

import datetime

from obsidian_kanban_parser import parse
from tests.helpers import get_lane, make_board, make_item, make_lane

# ---------------------------------------------------------------------------
# find_items_by_tag
# ---------------------------------------------------------------------------


def test_find_items_by_tag_single_match() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Fix bug #backend")))
    board = parse(md)

    # act
    results = board.find_items_by_tag("#backend")

    # assert
    assert len(results) == 1
    _, item = results[0]
    assert "#backend" in item.title_raw


def test_find_items_by_tag_multiple_matches_across_lanes() -> None:
    # arrange
    md = make_board(
        make_lane("Todo", make_item("Task A #urgent")),
        make_lane("In Progress", make_item("Task B #urgent")),
    )
    board = parse(md)

    # act
    results = board.find_items_by_tag("#urgent")

    # assert
    assert len(results) == 2
    titles = [item.title_raw for _, item in results]
    assert any("Task A" in t for t in titles)
    assert any("Task B" in t for t in titles)


def test_find_items_by_tag_no_match_returns_empty_list() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task without tags")))
    board = parse(md)

    # act
    results = board.find_items_by_tag("#nonexistent")

    # assert
    assert results == []


def test_find_items_by_tag_without_hash_prefix() -> None:
    # arrange — tag passed without leading #
    md = make_board(make_lane("Todo", make_item("Task #feature")))
    board = parse(md)

    # act
    results = board.find_items_by_tag("feature")

    # assert
    assert len(results) == 1


# ---------------------------------------------------------------------------
# find_items_by_inline_field
# ---------------------------------------------------------------------------


def test_find_items_by_inline_field_key_only() -> None:
    # arrange
    md = make_board(
        make_lane(
            "Todo",
            make_item("Task A [due::2024-06-01]"),
            make_item("Task B [priority::high]"),
        )
    )
    board = parse(md)

    # act
    results = board.find_items_by_inline_field("due")

    # assert
    assert len(results) == 1
    _, item = results[0]
    assert item.inline_fields["due"] == datetime.date(2024, 6, 1)


def test_find_items_by_inline_field_key_and_value() -> None:
    # arrange
    md = make_board(
        make_lane(
            "Todo",
            make_item("Task A [priority::high]"),
            make_item("Task B [priority::low]"),
        )
    )
    board = parse(md)

    # act
    results = board.find_items_by_inline_field("priority", "high")

    # assert
    assert len(results) == 1
    _, item = results[0]
    assert "Task A" in item.title_raw


def test_find_items_by_inline_field_no_match_returns_empty_list() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task [priority::low]")))
    board = parse(md)

    # act
    results = board.find_items_by_inline_field("due")

    # assert
    assert results == []


# ---------------------------------------------------------------------------
# board.lane (replaces find_lane_by_name)
# ---------------------------------------------------------------------------


def test_board_lane_exists() -> None:
    # arrange
    md = make_board(make_lane("Backlog"), make_lane("In Progress"))
    board = parse(md)

    # act
    lane = board.lane("In Progress")

    # assert
    assert lane is not None
    assert lane.title == "In Progress"


def test_board_lane_not_found_returns_none() -> None:
    # arrange
    md = make_board(make_lane("Todo"))
    board = parse(md)

    # act
    lane = board.lane("Nonexistent")

    # assert
    assert lane is None


# ---------------------------------------------------------------------------
# Dunder methods — KanbanLane
# ---------------------------------------------------------------------------


def test_item_in_lane() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("A")))
    board = parse(md)
    lane = get_lane(board, "Todo")
    item = lane.items[0]

    # assert
    assert item in lane


def test_item_not_in_lane() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("A")), make_lane("Done"))
    board = parse(md)
    item = get_lane(board, "Todo").items[0]
    done_lane = get_lane(board, "Done")

    # assert
    assert item not in done_lane


def test_len_lane() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("A"), make_item("B"), make_item("C")))
    board = parse(md)

    # assert
    assert len(get_lane(board, "Todo")) == 3


def test_getitem_lane() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("A"), make_item("B")))
    board = parse(md)
    lane = get_lane(board, "Todo")

    # assert
    assert lane[0].title_raw == "A"
    assert lane[1].title_raw == "B"


# ---------------------------------------------------------------------------
# Dunder methods — KanbanBoard
# ---------------------------------------------------------------------------


def test_iter_board() -> None:
    # arrange
    md = make_board(make_lane("Todo"), make_lane("Done"))
    board = parse(md)

    # act
    titles = [lane.title for lane in board]

    # assert
    assert titles == ["Todo", "Done"]


def test_len_board() -> None:
    # arrange
    md = make_board(make_lane("Todo"), make_lane("In Progress"), make_lane("Done"))
    board = parse(md)

    # assert
    assert len(board) == 3


def test_getitem_board_by_str() -> None:
    # arrange
    md = make_board(make_lane("Todo"), make_lane("Done"))
    board = parse(md)

    # assert
    assert board["Todo"].title == "Todo"
    assert board["Done"].title == "Done"


def test_getitem_board_by_str_missing_raises_keyerror() -> None:
    # arrange
    md = make_board(make_lane("Todo"))
    board = parse(md)

    # assert
    try:
        _ = board["Nonexistent"]
        raise AssertionError("Expected KeyError")
    except KeyError:
        pass


def test_getitem_board_by_int() -> None:
    # arrange
    md = make_board(make_lane("Todo"), make_lane("Done"))
    board = parse(md)

    # assert
    assert board[0].title == "Todo"
    assert board[1].title == "Done"


# ---------------------------------------------------------------------------
# Iteration
# ---------------------------------------------------------------------------


def test_iterate_items_in_lane() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("A"), make_item("B"), make_item("C")))
    board = parse(md)

    # act
    titles = [item.title_raw for item in get_lane(board, "Todo")]

    # assert
    assert titles == ["A", "B", "C"]


# ---------------------------------------------------------------------------
# subtasks via item.subtasks
# ---------------------------------------------------------------------------


def test_get_subtasks_returns_checked_and_unchecked() -> None:
    # arrange
    md = make_board(make_lane("Backlog", make_item("Epic\n- [ ] Step 1\n- [x] Step 2")))
    board = parse(md)

    # act
    subtasks = get_lane(board, "Backlog").items[0].subtasks

    # assert
    assert subtasks == [(False, "Step 1"), (True, "Step 2")]
