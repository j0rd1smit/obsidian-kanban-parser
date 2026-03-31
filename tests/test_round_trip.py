"""Round-trip fidelity tests.

Each test asserts that parse(md) → write() produces the exact same markdown
string — ensuring the library never silently reformats or drops content.

The arrange step uses markdown builders from ``tests.helpers`` so that expected
output is never written as a raw string (except for the full legacy fixture
that is intentionally kept as a regression anchor).
"""

import pytest

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
]


@pytest.mark.parametrize("description,md", _ROUND_TRIP_CASES, ids=[c[0] for c in _ROUND_TRIP_CASES])
def test_round_trip(description: str, md: str) -> None:
    # act
    output_md = parse_and_write(md)

    # assert
    assert_markdown_is_equal(output_md, md)


# ---------------------------------------------------------------------------
# Full legacy fixture — regression anchor for the complete canonical example
# ---------------------------------------------------------------------------

_FULL_BOARD = make_board(
    make_lane("Completed", make_item("Completed 1", checked=True), make_item("Completed 2", checked=True), mark_complete=True),
    make_lane("Active", make_item("Active 1"), wip_limit=3),
    make_lane("Scheduled", make_item("Scheduled 1"), wip_limit=5),
    make_lane("Waiting for", make_item("Waiting for 1")),
    make_lane("To Discuss"),
    make_lane(
        "Back burner",
        make_item("back burner 1"),
        make_item("back burner 2\n- [ ] back burner 2a\n- [ ] back burner 2b"),
        make_item("back burner 3"),
    ),
    make_lane("Clarify", make_item("Some Clarify task")),
    archive=[make_item("Task 1", checked=True), make_item("Task 2", checked=True)],
    settings={
        "kanban-plugin": "board",
        "new-note-folder": "01 Projects/Xebia/Tasks",
        "show-add-list": True,
        "list-collapse": [None, False, None],
        "show-checkboxes": True,
    },
)

# The canonical string from the original smoketest — kept verbatim so that any
# unintended format drift is caught as a test failure.
_LEGACY_FIXTURE = """---

kanban-plugin: board

---

## Completed

**Complete**
- [x] Completed 1
- [x] Completed 2


## Active (3)

- [ ] Active 1


## Scheduled (5)

- [ ] Scheduled 1


## Waiting for

- [ ] Waiting for 1


## To Discuss



## Back burner

- [ ] back burner 1
- [ ] back burner 2
    - [ ] back burner 2a
    - [ ] back burner 2b
- [ ] back burner 3


## Clarify

- [ ] Some Clarify task


***

## Archive

- [x] Task 1
- [x] Task 2

%% kanban:settings

```
{"kanban-plugin":"board","new-note-folder":"01 Projects/Xebia/Tasks","show-add-list":true,"list-collapse":[null,false,null],"show-checkboxes":true}
```

%%
""".lstrip()


def test_full_board_builder_matches_legacy_fixture() -> None:
    """The board produced by the builders must equal the legacy raw string."""
    assert _FULL_BOARD == _LEGACY_FIXTURE


def test_full_board_round_trips() -> None:
    """The full complex board must survive a parse → write cycle unchanged."""
    # act
    output_md = parse_and_write(_FULL_BOARD)

    # assert
    assert_markdown_is_equal(output_md, _FULL_BOARD)
