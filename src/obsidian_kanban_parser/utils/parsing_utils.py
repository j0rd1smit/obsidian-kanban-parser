import re

_BLOCK_ID_RE = re.compile(r"\s+\^([a-zA-Z0-9\-_]+)$")
_LANE_WIP_RE = re.compile(r"^(.*?)\s*\((\d+)\)$")


def _indent_newlines(s: str, use_tab: bool = False, indent: str | None = None) -> str:
    """Mirror of indentNewLines(): indent continuation lines with 4 spaces (or tab).

    Blank continuation lines are kept blank (no trailing indent added).
    """
    if indent is None:
        indent = "\t" if use_tab else "    "
    lines = s.strip().split("\n")
    result = [lines[0]]
    for line in lines[1:]:
        result.append(f"{indent}{line}" if line else "")
    return "\n".join(result)


def _dedent_newlines(s: str, indent: str = "    ") -> str:
    """Mirror of dedentNewLines(): strip the indent prefix from continuation lines."""
    return re.sub(r"\n" + re.escape(indent), "\n", s.strip())


def _replace_brs(s: str) -> str:
    """Mirror of replaceBrs(): convert <br> back to newlines."""
    return s.replace("<br>", "\n").strip()


def _replace_newlines(s: str) -> str:
    """Mirror of replaceNewLines(): convert newlines to <br> for storage in headings."""
    return s.strip().replace("\r\n", "<br>").replace("\n", "<br>")


def _lane_title_with_max_items(title: str, max_items: int) -> str:
    if max_items:
        return f"{title} ({max_items})"
    return title
