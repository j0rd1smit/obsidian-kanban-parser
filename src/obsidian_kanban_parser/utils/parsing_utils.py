import re

_BLOCK_ID_RE = re.compile(r"\s+\^([a-zA-Z0-9\-_]+)$")
_LANE_WIP_RE = re.compile(r"^(.*?)\s*\((\d+)\)$")


def _indent_newlines(s: str, use_tab: bool = False) -> str:
    """Mirror of indentNewLines(): indent continuation lines with 4 spaces (or tab)."""
    indent = "\t" if use_tab else "    "
    return s.strip().replace("\n", f"\n{indent}")


def _dedent_newlines(s: str) -> str:
    """Mirror of dedentNewLines(): strip the 4-space / tab indent from continuation lines."""
    return re.sub(r"\n(?: {4}|\t)", "\n", s.strip())


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
