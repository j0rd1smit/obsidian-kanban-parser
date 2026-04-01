from pathlib import Path

import pytest

from .helpers import make_board, make_item, make_lane


@pytest.fixture()
def full_board_raw() -> str:
    path = Path(__file__).parent / "resources" / "full-board.md"
    return path.read_text(encoding="utf-8")


def test_full_board_builder_matches_full_board_raw_fixture(full_board_raw: str) -> None:
    """The board produced by the builders must equal the legacy raw string."""
    _full_board = make_board(
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

    assert _full_board == full_board_raw
