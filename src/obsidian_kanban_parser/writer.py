import json

import yaml

from obsidian_kanban_parser.domain import KanbanBoard, KanbanItem, KanbanLane
from obsidian_kanban_parser.utils.parsing_utils import _indent_newlines, _lane_title_with_max_items, _replace_newlines


def _item_to_md(item: KanbanItem, use_tab: bool = False) -> str:
    """Mirror of itemToMd() in list.ts."""
    body = _indent_newlines(item.content, use_tab)
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
    # Use the preserved raw JSON string for byte-for-byte fidelity.
    json_str = board._settings_raw if board._settings_raw is not None else json.dumps(board.settings, separators=(",", ":"))
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
