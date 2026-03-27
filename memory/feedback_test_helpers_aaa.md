---
name: Test helpers must respect arrange-act-assert separation
description: Assertion helpers accept resolved objects, not raw markdown; callers own the arrange/act steps
type: feedback
---

Assertion helpers must accept already-resolved domain objects (`KanbanBoard`, `KanbanLane`) rather than raw markdown strings. Callers are responsible for parsing and resolving (arrange + act) before passing to an assertion helper.

**Why:** Bundling parse/find inside assertion helpers hides test-case-specific information, makes helpers less reusable, and conflates arrange, act, and assert phases. The user wants helpers that are small, composable, and easy to read at the call site.

**How to apply:**
- `assert_item_in_lane(lane, fragment)` — caller resolves the lane first via `find_lane_by_name`
- `assert_item_in_archive(board, fragment)` — caller holds the board
- For round-trip tests: `output_md = parse_and_write(md)` (act), then `assert_markdown_is_equal(output_md, md)` (assert) — never `assert_round_trips(md)` which hides the act step
