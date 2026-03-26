import re
from collections.abc import Iterator
from dataclasses import dataclass, field


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

    def inline_field(self, key: str) -> str | None:
        """Return the value of [key::value] or (key::value) in title_raw."""
        pat = rf"[\[\(]{re.escape(key)}::([^\]\)]+)[\]\)]"
        m = re.search(pat, self.title_raw)
        return m.group(1).strip() if m else None

    def set_inline_field(self, key: str, value: str) -> None:
        """Update an existing [key::value] field in title_raw, or append it."""
        pat = rf"([\[\(]){re.escape(key)}::([^\]\)]+)([\]\)])"

        def replacement(m: re.Match) -> str:
            return f"{m.group(1)}{key}::{value}{m.group(3)}"

        new, count = re.subn(pat, replacement, self.title_raw)
        if count:
            self.title_raw = new
        else:
            self.title_raw = self.title_raw.rstrip() + f" [{key}::{value}]"

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
