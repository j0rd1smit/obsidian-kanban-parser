"""Test helpers: markdown builders and assertion utilities.

Builders mirror the writer's serialisation logic exactly, so that
``assert_markdown_is_equal(parse_and_write(make_board(...)), make_board(...))``
always holds and tests stay decoupled from internal implementation details.

Assertion helpers are intentionally small and accept already-resolved objects
(boards, lanes) rather than raw markdown strings.  Callers are responsible for
the arrange/act steps (parse, board.lane(), etc.) so that each helper
stays composable and the test body makes every step explicit.
"""

from __future__ import annotations

import json
from typing import Any

from obsidian_kanban_parser import parse, write
from obsidian_kanban_parser.domain import KanbanBoard, KanbanLane


def make_frontmatter(extra: dict[str, Any] | None = None) -> str:
    """Return a raw frontmatter string with ``kanban-plugin: board`` plus any extra fields.

    Use this to avoid writing raw ``---\\n\\n...\\n\\n---\\n`` strings in tests.

    Example::

        make_frontmatter({"custom-field": "my-value"})
        # "---\\n\\nkanban-plugin: board\\ncustom-field: my-value\\n\\n---\\n"
    """
    fields = {"kanban-plugin": "board", **(extra or {})}
    lines = "\n".join(f"{k}: {v}" for k, v in fields.items())
    return f"---\n\n{lines}\n\n---\n"


# ---------------------------------------------------------------------------
# Markdown builders
# Each builder mirrors the corresponding _*_to_md helper in writer.py so that
# make_board(...) == write(parse(make_board(...))).
# ---------------------------------------------------------------------------


def make_item(
    content: str,
    *,
    checked: bool = False,
    block_id: str | None = None,
) -> str:
    """Return a single item line as the writer would produce it.

    *content* uses ``\\n`` for embedded content lines (e.g. subtasks) in
    their un-indented, canonical form — exactly what ``KanbanItem.content``
    stores.  Continuation lines are indented with 4 spaces in the output,
    mirroring ``_item_to_md`` / ``_indent_newlines`` in writer.py.
    """
    check_char = "x" if checked else " "
    # Mirror _indent_newlines: strip then re-indent continuation lines.
    body = content.strip().replace("\n", "\n    ")
    if block_id:
        nl = body.find("\n")
        if nl == -1:
            body = f"{body} ^{block_id}"
        else:
            body = f"{body[:nl]} ^{block_id}{body[nl:]}"
    return f"- [{check_char}] {body}"


def make_lane(
    title: str,
    *item_mds: str,
    wip_limit: int = 0,
    mark_complete: bool = False,
) -> str:
    """Return a lane section as the writer would produce it.

    *item_mds* are strings returned by :func:`make_item`.  The trailing three
    blank-line separator is included, mirroring ``_lane_to_md`` in writer.py.
    """
    heading = f"{title} ({wip_limit})" if wip_limit else title
    lines: list[str] = [f"## {heading}", ""]
    if mark_complete:
        lines.append("**Complete**")
    lines.extend(item_mds)
    # Three trailing empty strings produce the two blank lines between lanes.
    lines += ["", "", ""]
    return "\n".join(lines)


def make_board(
    *lane_mds: str,
    frontmatter: str | None = None,
    settings: dict | None = None,
    archive: list[str] | None = None,
) -> str:
    """Return a complete board markdown string as the writer would produce it.

    Args:
        *lane_mds: Lane sections from :func:`make_lane`.
        frontmatter: Raw frontmatter string (must end with ``\\n``).  Defaults
            to the standard Obsidian Kanban header.  Pass ``""`` to omit.
        settings: Dict serialised into a ``%% kanban:settings %%`` block.
        archive: Item markdown strings (from :func:`make_item`) for the
            archive section.
    """
    fm = make_frontmatter() if frontmatter is None else frontmatter
    lanes_md = "".join(lane_mds)

    archive_md = ""
    if archive:
        archive_lines = ["***", "", "## Archive", ""]
        archive_lines.extend(archive)
        archive_md = "\n".join(archive_lines)

    settings_md = ""
    if settings is not None:
        json_str = json.dumps(settings, separators=(",", ":"))
        settings_md = f"\n\n%% kanban:settings\n```\n{json_str}\n```\n%%"

    # write() produces: frontmatter_raw + "\n" + lanes + archive + settings
    return fm + "\n" + lanes_md + archive_md + settings_md


# ---------------------------------------------------------------------------
# Assertion helpers
# ---------------------------------------------------------------------------


def parse_and_write(md: str) -> str:
    """Act helper: parse markdown and immediately write it back."""
    return write(parse(md))


def assert_markdown_is_equal(one: str, other: str) -> None:
    """Assert that two markdown strings are identical."""
    assert one == other, f"different output.\n\n--- expected ---\n{other!r}\n\n--- got ---\n{one!r}"


def assert_item_in_lane(lane: KanbanLane, item_fragment: str) -> None:
    """Assert that *lane* contains an item matching *item_fragment*."""
    titles = [item.content for item in lane]
    assert any(item_fragment in t for t in titles), (
        f"No item containing {item_fragment!r} found in lane.\nItems present: {titles}"
    )


def assert_item_not_in_lane(lane: KanbanLane, item_fragment: str) -> None:
    """Assert that no item in *lane* matches *item_fragment*."""
    titles = [item.content for item in lane]
    assert not any(item_fragment in t for t in titles), (
        f"Item containing {item_fragment!r} was unexpectedly found in lane.\nItems present: {titles}"
    )


def assert_item_in_archive(board: KanbanBoard, item_fragment: str) -> None:
    """Assert that an archived item matching *item_fragment* exists in *board*."""
    titles = [item.content for item in board.archive]
    assert any(item_fragment in t for t in titles), (
        f"No archived item containing {item_fragment!r} found.\nArchived items: {titles}"
    )


def assert_item_not_in_archive(board: KanbanBoard, item_fragment: str) -> None:
    """Assert that no archived item in *board* matches *item_fragment*."""
    titles = [item.content for item in board.archive]
    assert not any(item_fragment in t for t in titles), (
        f"Archived item containing {item_fragment!r} was unexpectedly found.\nArchived items: {titles}"
    )


def get_lane(board: KanbanBoard, title: str) -> KanbanLane:
    """Return the named lane; fail the test immediately if it doesn't exist.

    Use this in arrange/act steps to skip the repetitive
    ``assert lane is not None`` boilerplate.
    """
    lane = board.lane(title)
    assert lane is not None, f"Lane {title!r} not found in board"
    return lane
