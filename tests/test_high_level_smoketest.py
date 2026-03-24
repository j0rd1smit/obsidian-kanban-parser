import pytest

from obsidian_kanban_parser import find_lane_by_name, parse, write

_EXAMPLE_FILE_CONTENT = """
---

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
{"kanban-plugin":"board"}
```
%%
""".strip()


def test_parse_and_write_should_not_change_content() -> None:
    board = parse(_EXAMPLE_FILE_CONTENT)
    output = write(board)
    assert output == _EXAMPLE_FILE_CONTENT


@pytest.mark.parametrize(
    "lane_name,expected_tasks",
    [
        ("Waiting for", ["Waiting for 1"]),
        ("Scheduled", ["Scheduled 1"]),
        ("Completed", ["Completed 1", "Completed 2"]),
        ("Active", ["Active 1"]),
    ],
)
def test_parse_find_expected_tasks(
    lane_name: str,
    expected_tasks: list[str],
) -> None:
    board = parse(_EXAMPLE_FILE_CONTENT)

    lane = find_lane_by_name(board, lane_name)
    assert lane is not None, f"Lane '{lane_name}' not found"
    for task in lane:
        assert task.title_raw in expected_tasks, f"Task '{task.title_raw}' not present in '{expected_tasks}'"
