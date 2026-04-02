import json
import re

import yaml

from obsidian_kanban_parser.domain import KanbanBoard, KanbanItem, KanbanLane
from obsidian_kanban_parser.utils.parsing_utils import _indent_newlines, _lane_title_with_max_items, _replace_newlines


def _fix_tag_before_subtask(content: str) -> str:
    """Add trailing space to any line ending with a tag immediately followed by a subtask.

    Obsidian fails to render subtasks when the preceding line ends with a bare tag
    (e.g. ``#project/foo``) and has no trailing space.  This mirrors the Obsidian
    plugin behaviour of emitting a trailing space in that case.
    Only lines that *immediately* precede a subtask line are affected.
    """
    lines = content.split("\n")
    result = []
    for i, line in enumerate(lines):
        if (
            i + 1 < len(lines)
            and re.search(r"#\S+$", line)  # ends with a tag
            and re.match(r"^- \[.\]", lines[i + 1])  # next line is a subtask
        ):
            result.append(line + " ")
        else:
            result.append(line)
    return "\n".join(result)


def _item_to_md(item: KanbanItem, use_tab: bool = False) -> str:
    """Mirror of itemToMd() in list.ts."""
    indent = "\t" if use_tab else item._indent
    body = _indent_newlines(_fix_tag_before_subtask(item.content), indent=indent)
    if item.block_id:
        # Block ID appended to first line only.
        nl = body.find("\n")
        if nl == -1:
            body = body + " ^" + item.block_id
        else:
            body = body[:nl] + " ^" + item.block_id + body[nl:]
    return f"- [{item.check_char}] {body}"


def _lane_to_md(lane: KanbanLane, use_tab: bool = False) -> str:
    """Mirror of laneToMd() in list.ts."""
    heading = _replace_newlines(_lane_title_with_max_items(lane.title, lane.max_items))
    lines: list[str] = [f"## {heading}", ""]

    if lane.should_mark_complete:
        lines.append("**Complete**")

    for item in lane.items:
        lines.append(_item_to_md(item, use_tab))

    # Three trailing empty strings → two blank lines after last item.
    lines += ["", "", ""]
    return "\n".join(lines)


def _archive_to_md(archive: list[KanbanItem], use_tab: bool = False) -> str:
    """Mirror of archiveToMd() in list.ts."""
    if not archive:
        return ""
    lines = ["***", "", "## Archive", ""]
    for item in archive:
        lines.append(_item_to_md(item, use_tab))
    return "\n".join(lines)


def _settings_to_md(board: KanbanBoard) -> str:
    """Mirror of settingsToCodeblock() in common.ts."""
    if board.settings is None:
        return ""
    # Use the preserved raw block for byte-for-byte fidelity.
    if board._settings_raw is not None:
        return "\n\n" + board._settings_raw
    json_str = json.dumps(board.settings, separators=(",", ":"))
    return "\n".join(["", "", "%% kanban:settings", "", "```", json_str, "```", "", "%%", ""])


def _frontmatter_to_md(board: KanbanBoard) -> str:
    """Return frontmatter block.  Uses raw text when available for round-trip fidelity."""
    if board._frontmatter_raw:
        return board._frontmatter_raw

    yaml_str = yaml.dump(board.frontmatter, default_flow_style=False, allow_unicode=True)

    return f"---\n\n{yaml_str}\n---\n\n"


def write(board: KanbanBoard, use_tab: bool = False) -> str:
    """Serialize a KanbanBoard back to the Obsidian Kanban markdown format."""
    lanes_md = "".join(_lane_to_md(ln, use_tab) for ln in board.lanes)
    return _frontmatter_to_md(board) + "\n" + lanes_md + _archive_to_md(board.archive, use_tab) + _settings_to_md(board)
