"""Round-trip fidelity tests.

Each test asserts that parse(md) → write() produces the exact same markdown
string — ensuring the library never silently reformats or drops content.

The arrange step uses markdown builders from ``tests.helpers`` so that expected
output is never written as a raw string (except for the full legacy fixture
that is intentionally kept as a regression anchor).
"""

import pytest

from obsidian_kanban_parser import parse, write
from tests.helpers import assert_markdown_is_equal, make_board, make_item, make_lane, parse_and_write

# ---------------------------------------------------------------------------
# Parametrised cases — simple, isolated feature scenarios
# ---------------------------------------------------------------------------

_ROUND_TRIP_CASES: list[tuple[str, str]] = [
    (
        "minimal board — single empty lane",
        make_board(make_lane("Todo")),
    ),
    (
        "single lane with items",
        make_board(make_lane("Todo", make_item("Task 1"), make_item("Task 2"))),
    ),
    (
        "checked and unchecked items in the same lane",
        make_board(
            make_lane(
                "Done",
                make_item("Finished task", checked=True),
                make_item("Still pending"),
                mark_complete=True,
            )
        ),
    ),
    (
        "items with hashtags",
        make_board(make_lane("Todo", make_item("Fix bug #backend #urgent"))),
    ),
    (
        "items with inline fields",
        make_board(make_lane("Todo", make_item("Schedule meeting [due::2024-06-01] [priority::high]"))),
    ),
    (
        "lane with WIP limit",
        make_board(make_lane("In Progress", make_item("Work item"), wip_limit=3)),
    ),
    (
        "lane with mark_complete flag",
        make_board(make_lane("Completed", make_item("Done", checked=True), mark_complete=True)),
    ),
    (
        "item with block ID",
        make_board(make_lane("Todo", make_item("Important task", block_id="abc123"))),
    ),
    (
        "item with subtasks",
        make_board(
            make_lane(
                "Backlog",
                make_item("Epic\n- [ ] Sub-task A\n- [x] Sub-task B"),
            )
        ),
    ),
    (
        "multiple lanes",
        make_board(
            make_lane("Backlog", make_item("Idea")),
            make_lane("In Progress", make_item("WIP"), wip_limit=2),
            make_lane("Done", make_item("Shipped", checked=True), mark_complete=True),
        ),
    ),
    (
        "empty archive section",
        make_board(
            make_lane("Todo", make_item("Active task")),
            archive=[make_item("Old task", checked=True)],
        ),
    ),
    (
        "settings block",
        make_board(
            make_lane("Todo"),
            settings={"kanban-plugin": "board"},
        ),
    ),
    (
        "archive and settings together",
        make_board(
            make_lane("Todo", make_item("Current")),
            archive=[make_item("Past", checked=True)],
            settings={"kanban-plugin": "board"},
        ),
    ),
    (
        "multiple items with mixed features",
        make_board(
            make_lane(
                "Sprint",
                make_item("Task A #feature [est::3d]", block_id="t1"),
                make_item("Task B #bug", checked=True),
                make_item("Task C\n- [ ] step 1\n- [ ] step 2"),
                wip_limit=5,
            )
        ),
    ),
    (
        "tag immediately before subtask — trailing space preserved on round-trip",
        make_board(make_lane("Todo", make_item("Task: #my-tag\n- [ ] Sub-task"))),
    ),
    (
        "tag with non-subtask continuation before subtask — no trailing space",
        make_board(make_lane("Todo", make_item("Task: #my-tag\nsome note\n- [ ] Sub-task"))),
    ),
    (
        "line ending with inline-field bracket before subtask — no trailing space",
        make_board(make_lane("Todo", make_item("Task: #tag1 #tag2 [scheduled:: 2026-04-01]\n- [ ] Sub-task"))),
    ),
    (
        "tag with existing trailing space before subtask — no double space",
        make_board(make_lane("Todo", make_item("Task: #my-tag \n- [ ] Sub-task"))),
    ),
]


@pytest.mark.parametrize("description,md", _ROUND_TRIP_CASES, ids=[c[0] for c in _ROUND_TRIP_CASES])
def test_round_trip(description: str, md: str) -> None:
    # act
    output_md = parse_and_write(md)

    # assert
    assert_markdown_is_equal(output_md, md)


def test_write_adds_trailing_space_after_tag_before_subtask() -> None:
    """Writer must add trailing space when a tag is immediately followed by a subtask.

    Obsidian does not render the subtask list when the preceding line ends with a
    bare ``#tag`` and no trailing space.  This test verifies the fix fires even when
    the source markdown lacks the space (e.g. user-edited files).
    """
    # arrange — raw item built without trailing space after the tag
    raw_item = "- [ ] Task: #my-tag\n    - [ ] Sub-task"
    raw_md = make_board(make_lane("Todo", raw_item))
    board = parse(raw_md)

    # act
    result_md = write(board)

    # assert — writer must add the trailing space
    expected_md = make_board(make_lane("Todo", make_item("Task: #my-tag\n- [ ] Sub-task")))
    assert_markdown_is_equal(result_md, expected_md)
