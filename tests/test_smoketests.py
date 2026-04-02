from pathlib import Path

import pytest

from obsidian_kanban_parser import KanbanBoard, KanbanItem, SubTask, parse, write

from .helpers import assert_markdown_is_equal, parse_and_write

_RESOURCES_FOLDER = Path(__file__).parent / "resources"


def _load_markdown_resource(file_name: str) -> str:
    path = _RESOURCES_FOLDER / file_name
    return path.read_text(encoding="utf-8")


def _find_all_markdown_resources() -> list[str]:
    return [f.name for f in _RESOURCES_FOLDER.glob("*.md")]


@pytest.mark.parametrize(
    "file_name",
    _find_all_markdown_resources(),
)
def test_full_board_round_trips(file_name: str) -> None:
    """The full complex board in resources survive a parse → write cycle unchanged."""
    content = _load_markdown_resource(file_name)

    # act
    output_md = parse_and_write(content)

    # assert
    assert_markdown_is_equal(output_md, content)


def test_subtasks_are_parsed_correctly_for_tasks_with_text_description() -> None:
    # arange
    content = _load_markdown_resource("item-with-text-description-and-subtasks.md")
    expected_subtasks = [
        SubTask(text="subtask 1", checked=False),
        SubTask(text="subtask 2", checked=True),
        SubTask(text="subtask 3", checked=False),
        SubTask(text="subtask 4", checked=False),
    ]

    # Act
    board = parse(content)
    item = _find_item_that_contains_text(board, "Task with text description and subtasks")

    # assert
    assert item.subtasks == expected_subtasks


def _find_item_that_contains_text(board: KanbanBoard, text: str) -> KanbanItem:
    for lane in board:
        for item in lane:
            if text in item.content:
                return item

    raise AssertionError(f"No item found containing text: {text!r}")


def test_new_inline_field_should_be_added_on_the_first_line() -> None:
    # arange
    content = """
---

kanban-plugin: board

---

## some list

- [ ] Normal task [due:: 2025-06-14]
- [ ] Normal task with subtasks
  - [ ] Subtask 1 [label:: hello]
  - [ ] Subtask 2

""".strip()
    expected = """
---

kanban-plugin: board

---

## some list

- [ ] Normal task [due:: 2025-06-14] [completion:: 2025-06-14]
- [ ] Normal task with subtasks [completion:: 2025-06-14]
  - [ ] Subtask 1 [label:: hello]
  - [ ] Subtask 2

""".strip()

    # act
    board = parse(content)
    for lane in board:
        for item in lane:
            item.inline_fields["completion"] = "2025-06-14"
    output = write(board)

    # assert
    assert_markdown_is_equal(output, expected)


def test_new_tags_should_be_added_on_the_first_line() -> None:
    # arange
    content = """
---

kanban-plugin: board

---

## some list

- [ ] Normal task #important [due:: 2025-06-14]
- [ ] Normal task with subtasks
  - [ ] Subtask 1 [label:: hello]
  - [ ] Subtask 2 #something
- [ ] other task

""".strip()
    # Trailing space after #newtag is required: Obsidian does not render subtasks
    # when the preceding line ends with a bare tag and no trailing space.
    expected = (
        "---\n\nkanban-plugin: board\n\n---\n\n## some list\n\n"
        "- [ ] Normal task #important [due:: 2025-06-14] #newtag\n"
        "- [ ] Normal task with subtasks #newtag \n"
        "  - [ ] Subtask 1 [label:: hello]\n"
        "  - [ ] Subtask 2 #something\n"
        "- [ ] other task #newtag"
    )

    # act
    board = parse(content)
    for lane in board:
        for item in lane:
            item.tags.add("newtag")
    output = write(board)

    # assert
    assert_markdown_is_equal(output, expected)
