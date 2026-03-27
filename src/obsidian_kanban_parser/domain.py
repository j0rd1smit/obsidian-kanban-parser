from __future__ import annotations

import datetime
import re
from collections.abc import Iterator
from dataclasses import dataclass, field


class InlineFields:
    """Dict-like proxy over a KanbanItem's title_raw for [key::value] fields."""

    def __init__(self, item: KanbanItem) -> None:
        self._item = item

    @staticmethod
    def _pattern(key: str) -> re.Pattern:
        return re.compile(rf"[\[\(]{re.escape(key)}::([^\]\)]+)[\]\)]")

    @staticmethod
    def _pattern_with_delimiters(key: str) -> re.Pattern:
        return re.compile(rf"([\[\(]){re.escape(key)}::([^\]\)]+)([\]\)])")

    @staticmethod
    def _coerce(raw: str) -> datetime.date | int | float | str:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
            try:
                return datetime.date.fromisoformat(raw)
            except ValueError:
                pass
        try:
            return int(raw)
        except ValueError:
            pass
        try:
            return float(raw)
        except ValueError:
            pass
        return raw

    @staticmethod
    def _serialize(value: datetime.date | int | float | str) -> str:
        if isinstance(value, datetime.date):
            return value.isoformat()
        return str(value)

    def __getitem__(self, key: str) -> datetime.date | int | float | str | None:
        m = self._pattern(key).search(self._item.title_raw)
        if m is None:
            return None
        return self._coerce(m.group(1).strip())

    def __setitem__(self, key: str, value: datetime.date | int | float | str) -> None:
        serialized = self._serialize(value)
        pat = self._pattern_with_delimiters(key)

        def replacement(m: re.Match) -> str:
            return f"{m.group(1)}{key}::{serialized}{m.group(3)}"

        new, count = pat.subn(replacement, self._item.title_raw)
        if count:
            self._item.title_raw = new
        else:
            self._item.title_raw = self._item.title_raw.rstrip() + f" [{key}::{serialized}]"

    def __delitem__(self, key: str) -> None:
        pat = re.compile(rf"\s*[\[\(]{re.escape(key)}::[^\]\)]+[\]\)]")
        self._item.title_raw = pat.sub("", self._item.title_raw).rstrip()

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        return self._pattern(key).search(self._item.title_raw) is not None


@dataclass
class KanbanItem:
    """A single card/task on the board.

    ``title_raw`` is the exact markdown text of the item body (newlines as \\n,
    no block-id, no leading/trailing whitespace).  It is what the plugin stores
    in ``itemData.titleRaw`` and is the canonical source of truth for writing.

    Convenience properties parse metadata out of ``title_raw`` on the fly, so
    they always reflect the current state of the raw text.
    """

    title_raw: str
    check_char: str = " "  # ' '=unchecked, 'x'=checked, or custom char
    block_id: str | None = None

    def __post_init__(self) -> None:
        self.inline_fields = InlineFields(self)

    # ------------------------------------------------------------------
    # Convenience read-only properties
    # ------------------------------------------------------------------

    @property
    def checked(self) -> bool:
        return self.check_char.lower() == "x"

    @property
    def tags(self) -> list[str]:
        """All #tags found in title_raw, e.g. ['#bug', '#frontend']."""
        return re.findall(r"#[\w/\-]+", self.title_raw)

    def has_tag(self, tag: str) -> bool:
        """Case-sensitive check. Tag may be passed with or without leading #."""
        tag = tag if tag.startswith("#") else f"#{tag}"
        return tag in self.tags

    def add_tag(self, tag: str) -> None:
        tag = tag if tag.startswith("#") else f"#{tag}"
        if not self.has_tag(tag):
            self.title_raw = self.title_raw.rstrip() + f" {tag}"

    def remove_tag(self, tag: str) -> None:
        tag = tag if tag.startswith("#") else f"#{tag}"
        self.title_raw = re.sub(r"\s*" + re.escape(tag) + r"\b", "", self.title_raw).strip()

    def __repr__(self) -> str:
        status = "x" if self.checked else " "
        return f"KanbanItem([{status}] {self.title_raw!r})"


@dataclass
class KanbanLane:
    """A column on the board."""

    title: str
    items: list[KanbanItem] = field(default_factory=list)
    max_items: int = 0  # WIP limit; 0 = no limit
    should_mark_complete: bool = False

    def __iter__(self) -> Iterator[KanbanItem]:
        return iter(list(self.items))

    def __repr__(self) -> str:
        return f"KanbanLane({self.title!r}, {len(self.items)} items)"


@dataclass
class KanbanBoard:
    """The full Kanban board."""

    frontmatter: dict
    lanes: list[KanbanLane] = field(default_factory=list)
    archive: list[KanbanItem] = field(default_factory=list)

    # Per-board settings from the %% kanban:settings %% block (may be None).
    settings: dict | None = None

    # Raw strings preserved for round-trip fidelity — do not mutate directly.
    _frontmatter_raw: str = field(default="", repr=False)
    _settings_raw: str | None = field(default=None, repr=False)

    def lane(self, title: str) -> KanbanLane | None:
        """Return the first lane with the given title, or None."""
        for ln in self.lanes:
            if ln.title == title:
                return ln
        return None

    def __repr__(self) -> str:
        return (
            f"KanbanBoard({len(self.lanes)} lanes, "
            f"{sum(len(ln.items) for ln in self.lanes)} items, "
            f"{len(self.archive)} archived)"
        )
