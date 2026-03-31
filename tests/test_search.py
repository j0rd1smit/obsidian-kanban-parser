"""Search / read tests.

Each test arranges a known markdown input, calls a read/query API,
and asserts on the returned domain objects (not on raw markdown).
"""

from obsidian_kanban_parser import SubTask, parse
from tests.helpers import get_lane, make_board, make_item, make_lane

# ---------------------------------------------------------------------------
# board.lane
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
    assert lane[0].content == "A"
    assert lane[1].content == "B"


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
    titles = [item.content for item in get_lane(board, "Todo")]

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
    assert subtasks == [SubTask(checked=False, text="Step 1"), SubTask(checked=True, text="Step 2")]
