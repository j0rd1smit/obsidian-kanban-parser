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


class Tags:
    """Set-like proxy over a KanbanItem's title_raw for #tag operations."""

    def __init__(self, item: KanbanItem) -> None:
        self._item = item

    def _normalize(self, tag: str) -> str:
        return tag if tag.startswith("#") else f"#{tag}"

    def __iter__(self) -> Iterator[str]:
        return iter(re.findall(r"#[\w/\-]+", self._item.title_raw))

    def __contains__(self, tag: object) -> bool:
        if not isinstance(tag, str):
            return False
        return self._normalize(tag) in re.findall(r"#[\w/\-]+", self._item.title_raw)

    def __len__(self) -> int:
        return len(re.findall(r"#[\w/\-]+", self._item.title_raw))

    def __repr__(self) -> str:
        return f"Tags({list(self)!r})"

    def add(self, tag: str) -> None:
        """Idempotent — does nothing if the tag is already present."""
        tag = self._normalize(tag)
        if tag not in self:
            self._item.title_raw = self._item.title_raw.rstrip() + f" {tag}"

    def remove(self, tag: str) -> None:
        """Safe — does nothing if the tag is absent."""
        tag = self._normalize(tag)
        self._item.title_raw = re.sub(r"\s*" + re.escape(tag) + r"\b", "", self._item.title_raw).strip()


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
        self.tags = Tags(self)

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def checked(self) -> bool:
        return self.check_char.lower() == "x"

    @checked.setter
    def checked(self, value: bool) -> None:
        self.check_char = "x" if value else " "

    @property
    def subtasks(self) -> list[tuple[bool, str]]:
        """Return a list of (checked, text) for each sub-task line in title_raw."""
        results = []
        for m in re.finditer(r"\n- \[(.)\] (.+)", self.title_raw):
            results.append((m.group(1).lower() == "x", m.group(2)))
        return results

    def add_subtask(self, subtask_text: str, checked: bool = False) -> None:
        """Append a checklist sub-task line to title_raw."""
        char = "x" if checked else " "
        subtask_line = f"\n- [{char}] {subtask_text}"
        self.title_raw = self.title_raw.rstrip() + subtask_line

    def remove_subtask(self, subtask_text: str) -> bool:
        """Remove a sub-task line by matching its text. Returns True if removed."""
        pattern = re.compile(
            r"\n- \[.\] " + re.escape(subtask_text) + r"[ \t]*",
        )
        new, count = pattern.subn("", self.title_raw)
        if count:
            self.title_raw = new.rstrip()
            return True
        return False

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

    def __contains__(self, item: object) -> bool:
        return item in self.items

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> KanbanItem:
        return self.items[index]

    def __repr__(self) -> str:
        return f"KanbanLane({self.title!r}, {len(self.items)} items)"

    def add_item(self, title_raw: str, check_char: str = " ", position: int = -1) -> KanbanItem:
        """Create and insert a new item into this lane. Returns the new KanbanItem."""
        item = KanbanItem(title_raw=title_raw, check_char=check_char)
        if position < 0 or position >= len(self.items):
            self.items.append(item)
        else:
            self.items.insert(position, item)
        return item

    def remove_item(self, item: KanbanItem) -> bool:
        """Remove an item from this lane. Returns True on success."""
        if item not in self.items:
            return False
        self.items.remove(item)
        return True


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

    def __iter__(self) -> Iterator[KanbanLane]:
        return iter(list(self.lanes))

    def __len__(self) -> int:
        return len(self.lanes)

    def __getitem__(self, key: str | int) -> KanbanLane:
        if isinstance(key, int):
            return self.lanes[key]
        result = self.lane(key)
        if result is None:
            raise KeyError(key)
        return result

    def find_items_by_tag(self, tag: str) -> list[tuple[KanbanLane, KanbanItem]]:
        """Return [(lane, item), ...] for every item that has the given tag.

        ``tag`` may be passed with or without a leading #.
        """
        tag = tag if tag.startswith("#") else f"#{tag}"
        results = []
        for ln in self.lanes:
            for item in ln.items:
                if tag in item.tags:
                    results.append((ln, item))
        return results

    def find_items_by_inline_field(
        self,
        key: str,
        value: str | None = None,
    ) -> list[tuple[KanbanLane, KanbanItem]]:
        """Return [(lane, item), ...] where the item has [key::...] (optionally matching value)."""
        results = []
        for ln in self.lanes:
            for item in ln.items:
                v = item.inline_fields[key]
                if v is not None and (value is None or str(v) == value):
                    results.append((ln, item))
        return results

    def archive_item(self, item: KanbanItem, from_lane: KanbanLane) -> bool:
        """Remove item from a lane and append it to the archive. Returns True on success."""
        if item not in from_lane.items:
            return False
        from_lane.items.remove(item)
        self.archive.append(item)
        return True

    def unarchive_item(self, item: KanbanItem, to_lane: KanbanLane) -> bool:
        """Move an archived item back into a lane. Returns True on success."""
        if item not in self.archive:
            return False
        self.archive.remove(item)
        to_lane.items.append(item)
        return True

    def __repr__(self) -> str:
        return (
            f"KanbanBoard({len(self.lanes)} lanes, "
            f"{sum(len(ln.items) for ln in self.lanes)} items, "
            f"{len(self.archive)} archived)"
        )
