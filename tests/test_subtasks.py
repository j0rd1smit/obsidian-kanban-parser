"""Subtask operation tests.

Arrange markdown → parse → mutate subtasks → write → assert output markdown.
"""

from obsidian_kanban_parser import add_subtask, find_lane_by_name, get_subtasks, parse, remove_subtask, write

from tests.helpers import assert_markdown_is_equal, make_board, make_item, make_lane, parse_and_write


# ---------------------------------------------------------------------------
# get_subtasks
# ---------------------------------------------------------------------------


def test_get_subtasks_returns_checked_and_unchecked() -> None:
    # arrange
    md = make_board(make_lane("Backlog", make_item("Epic\n- [ ] Step 1\n- [x] Step 2")))
    board = parse(md)

    # act
    lane = find_lane_by_name(board, "Backlog")
    assert lane is not None
    item = lane.items[0]
    subtasks = get_subtasks(item)

    # assert
    assert subtasks == [(False, "Step 1"), (True, "Step 2")]


# ---------------------------------------------------------------------------
# add_subtask
# ---------------------------------------------------------------------------


def test_add_subtask_unchecked() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Epic")))
    board = parse(md)
    lane = find_lane_by_name(board, "Todo")
    assert lane is not None
    item = lane.items[0]

    # act
    add_subtask(item, "Sub-task A")
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Epic\n- [ ] Sub-task A")))
    assert_markdown_is_equal(result_md, expected_md)


def test_add_subtask_checked() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Epic")))
    board = parse(md)
    lane = find_lane_by_name(board, "Todo")
    assert lane is not None
    item = lane.items[0]

    # act
    add_subtask(item, "Done step", checked=True)
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Todo", make_item("Epic\n- [x] Done step")))
    assert_markdown_is_equal(result_md, expected_md)


# ---------------------------------------------------------------------------
# remove_subtask
# ---------------------------------------------------------------------------


def test_remove_subtask() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Epic\n- [ ] Step 1\n- [ ] Step 2")))
    board = parse(md)
    lane = find_lane_by_name(board, "Todo")
    assert lane is not None
    item = lane.items[0]

    # act
    result = remove_subtask(item, "Step 1")
    result_md = write(board)

    # assert
    assert result is True
    expected_md = make_board(make_lane("Todo", make_item("Epic\n- [ ] Step 2")))
    assert_markdown_is_equal(result_md, expected_md)


def test_remove_nonexistent_subtask_returns_false() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Epic\n- [ ] Step 1")))
    board = parse(md)
    lane = find_lane_by_name(board, "Todo")
    assert lane is not None
    item = lane.items[0]

    # act
    result = remove_subtask(item, "Nonexistent")

    # assert
    assert result is False


# ---------------------------------------------------------------------------
# Round-trip
# ---------------------------------------------------------------------------


def test_round_trip_item_with_multiple_subtasks() -> None:
    # arrange
    md = make_board(
        make_lane(
            "Backlog",
            make_item("Epic\n- [ ] Step 1\n- [x] Step 2\n- [ ] Step 3"),
        )
    )

    # act + assert
    assert_markdown_is_equal(parse_and_write(md), md)
