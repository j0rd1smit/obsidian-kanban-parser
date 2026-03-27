"""Lane property operation tests.

Arrange markdown → parse → mutate lane properties → write → assert output markdown.
"""

from obsidian_kanban_parser import parse, write
from tests.helpers import assert_markdown_is_equal, get_lane, make_board, make_item, make_lane

# ---------------------------------------------------------------------------
# WIP limit (max_items)
# ---------------------------------------------------------------------------


def test_read_lane_wip_limit() -> None:
    # arrange
    md = make_board(make_lane("In Progress", make_item("Task"), wip_limit=3))
    board = parse(md)

    # assert
    assert get_lane(board, "In Progress").max_items == 3


def test_update_wip_limit() -> None:
    # arrange
    md = make_board(make_lane("In Progress", make_item("Task"), wip_limit=3))
    board = parse(md)

    # act
    get_lane(board, "In Progress").max_items = 5
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("In Progress", make_item("Task"), wip_limit=5))
    assert_markdown_is_equal(result_md, expected_md)


def test_remove_wip_limit() -> None:
    # arrange
    md = make_board(make_lane("In Progress", make_item("Task"), wip_limit=3))
    board = parse(md)

    # act — setting to 0 removes the WIP annotation
    get_lane(board, "In Progress").max_items = 0
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("In Progress", make_item("Task")))
    assert_markdown_is_equal(result_md, expected_md)


# ---------------------------------------------------------------------------
# Lane title
# ---------------------------------------------------------------------------


def test_read_lane_title() -> None:
    # arrange
    md = make_board(make_lane("My Lane"))
    board = parse(md)

    # assert
    assert get_lane(board, "My Lane").title == "My Lane"


def test_update_lane_title() -> None:
    # arrange
    md = make_board(make_lane("Old Title", make_item("Task")))
    board = parse(md)

    # act
    get_lane(board, "Old Title").title = "New Title"
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("New Title", make_item("Task")))
    assert_markdown_is_equal(result_md, expected_md)


# ---------------------------------------------------------------------------
# should_mark_complete
# ---------------------------------------------------------------------------


def test_enable_mark_complete_on_lane() -> None:
    # arrange — lane without mark_complete
    md = make_board(make_lane("Done", make_item("Task", checked=True)))
    board = parse(md)

    # act
    get_lane(board, "Done").should_mark_complete = True
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Done", make_item("Task", checked=True), mark_complete=True))
    assert_markdown_is_equal(result_md, expected_md)


def test_disable_mark_complete_on_lane() -> None:
    # arrange — lane with mark_complete already set
    md = make_board(make_lane("Done", make_item("Task", checked=True), mark_complete=True))
    board = parse(md)

    # act
    get_lane(board, "Done").should_mark_complete = False
    result_md = write(board)

    # assert
    expected_md = make_board(make_lane("Done", make_item("Task", checked=True)))
    assert_markdown_is_equal(result_md, expected_md)
