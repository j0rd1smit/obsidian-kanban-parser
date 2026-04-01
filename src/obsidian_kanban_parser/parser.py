import json
import re

from obsidian_kanban_parser.domain import KanbanBoard, KanbanItem, KanbanLane
from obsidian_kanban_parser.utils.parsing_utils import _dedent_newlines, _replace_brs

_BLOCK_ID_RE = re.compile(r"\s+\^([a-zA-Z0-9\-_]+)$")
_LANE_WIP_RE = re.compile(r"^(.*?)\s*\((\d+)\)$")


def _split_list_items(text: str) -> list[str]:
    """Split a markdown list block into raw item strings (with continuation lines)."""
    items: list[str] = []
    current: str | None = None

    for line in text.split("\n"):
        if re.match(r"^- \[.\]", line):
            if current is not None:
                items.append(current)
            current = line
        elif current is not None and line and line[0] in (" ", "\t"):
            # Any indented line (spaces or tab) is a continuation of the current item.
            current += "\n" + line
        else:
            # Blank lines and non-indented non-item lines end the current item.
            if current is not None:
                items.append(current)
                current = None

    if current is not None:
        items.append(current)

    return items


def _detect_indent(raw: str) -> str:
    """Detect the indentation used on the first continuation line of a raw item."""
    for line in raw.split("\n")[1:]:
        if line and line[0] in (" ", "\t"):
            m = re.match(r"^([ \t]+)", line)
            if m:
                return m.group(1)
    return "    "  # default 4-space


def _parse_raw_item(raw: str) -> KanbanItem:
    """Parse a single raw list item string (e.g. '- [x] text\\n    cont') into a KanbanItem."""
    # raw starts with '- [x] '
    m = re.match(r"^- \[(.)\] (.*)", raw, re.DOTALL)
    if not m:
        return KanbanItem(content=raw)

    check_char = m.group(1)
    content = m.group(2)
    indent = _detect_indent(raw)
    content = _dedent_newlines(content, indent)

    # Block ID lives at the end of the first line only.
    nl = content.find("\n")
    first_line = content if nl == -1 else content[:nl]
    rest = "" if nl == -1 else content[nl:]

    block_id: str | None = None
    bid_m = _BLOCK_ID_RE.search(first_line)
    if bid_m:
        block_id = bid_m.group(1)
        first_line = first_line[: bid_m.start()]

    content = first_line + rest

    return KanbanItem(content=content, check_char=check_char, block_id=block_id, _indent=indent)


def _parse_items_block(block: str) -> list[KanbanItem]:
    return [_parse_raw_item(r) for r in _split_list_items(block)]


def parse(text: str) -> KanbanBoard:
    """Parse an Obsidian Kanban markdown file into a KanbanBoard.

    The original text is not modified; raw sub-strings are stored for
    round-trip fidelity.
    """

    # ---- 1. Strip %% kanban:settings %% block --------------------------------
    settings: dict | None = None
    settings_raw: str | None = None

    # Match both formats: with blank lines (full-board) and without (compact).
    # The leading \n\n is consumed so that text[: sm.start()] retains the
    # trailing newlines produced by the lane serialiser.
    settings_re = re.compile(
        r"\n\n(%% kanban:settings\n(?:\n)?```\n(.*?)\n```\n(?:\n)?%%\n?)",
        re.DOTALL,
    )
    sm = settings_re.search(text)
    if sm:
        settings_raw = sm.group(1)  # full block, used verbatim on write-back
        settings = json.loads(sm.group(2))
        text = text[: sm.start()]

    # ---- 2. Frontmatter -------------------------------------------------------
    frontmatter_raw = ""
    frontmatter: dict = {}

    fm_re = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
    fm_m = fm_re.match(text)
    if fm_m:
        frontmatter_raw = fm_m.group(0)
        try:
            import yaml  # soft dependency

            frontmatter = yaml.safe_load(fm_m.group(1)) or {}
        except ImportError:
            # Minimal fallback: parse simple key: value lines only.
            for line in fm_m.group(1).splitlines():
                kv = re.match(r"^(\S+):\s*(.*)", line)
                if kv:
                    frontmatter[kv.group(1)] = kv.group(2)
        body = text[fm_m.end() :]
    else:
        body = text

    # ---- 3. Split off archive (preceded by *** thematic break) ---------------
    archive_items: list[KanbanItem] = []
    main_body = body

    arch_split = re.split(r"\n\*\*\*\s*\n", body, maxsplit=1)
    if len(arch_split) == 2:
        main_body, archive_part = arch_split
        arch_heading = re.search(r"^##\s+Archive\s*\n", archive_part, re.MULTILINE)
        if arch_heading:
            archive_items = _parse_items_block(archive_part[arch_heading.end() :])

    # ---- 4. Parse lanes -------------------------------------------------------
    # Split on ## headings; prepend \n so the regex always matches at start.
    parts = re.split(r"\n(##\s+[^\n]+)", "\n" + main_body)
    # parts[0] = pre-heading content (ignored)
    # parts[1], parts[2] = heading, content, ...

    lanes: list[KanbanLane] = []
    i = 1
    while i < len(parts) - 1:
        heading = parts[i].strip()  # '## Title' or '## Title (n)'
        content = parts[i + 1]
        i += 2

        title_str = _replace_brs(heading[3:])  # strip '## '

        max_items = 0
        wip_m = _LANE_WIP_RE.match(title_str)
        if wip_m:
            title_str = wip_m.group(1)
            max_items = int(wip_m.group(2))

        should_mark_complete = bool(re.search(r"^\*\*Complete\*\*\s*$", content, re.MULTILINE))

        items = _parse_items_block(content)

        lanes.append(
            KanbanLane(
                title=title_str,
                items=items,
                max_items=max_items,
                should_mark_complete=should_mark_complete,
            )
        )

    return KanbanBoard(
        frontmatter=frontmatter,
        lanes=lanes,
        archive=archive_items,
        settings=settings,
        _frontmatter_raw=frontmatter_raw,
        _settings_raw=settings_raw,
    )
