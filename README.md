# obsidian-kanban-parser
This libray is a Python based parser and writer for Markdown files created by the [Obsidian Kanban plugin](https://github.com/obsidian-community/obsidian-kanban).
It purpose is to allow users to manipulate their Kanban boards programmatically, via Python based scripts, while ensuring the that resulting Markdown files remain fully compatible with the Obsidian plugin.


## Design Principles
- Round-trip fidelity: parsing and then writing a file should produce identical content, preserving formatting and metadata.
- To ensure compatibility with the Obsidian plugin, the library should mirror the plugin's own parsing and serialization logic as closely as possible (e.g. mimicking files like: [src/parsers/helpers/parser.ts](https://github.com/obsidian-community/obsidian-kanban/blob/main/src/parsers/helpers/parser.ts), [src/parsers/formats/list.ts](https://github.com/obsidian-community/obsidian-kanban/blob/main/src/parsers/formats/list.ts), [src/parsers/common.ts](https://github.com/obsidian-community/obsidian-kanban/blob/main/src/parsers/common.ts), , etc.).
- The library should provide a clean and well design API with properties such as:
  - Pythonic data structures.
  - There should only be a single way of doing things, and it should be the most intuitive way.
  - There should be a single source of truth for each piece of data.
  - The library should be designed with extensibility in mind.
  - The code must be easy to read and understand by both humans and machines (e.g. for LLMs).
  - The library should be well tested, with a comprehensive test suite covering all functionality and edge
  - The API exposed via the package should be stable and not expose internal implementation details or utilities that are not intended for public use.

### Testing principles
- Test cases should follow the arrange-act-assert pattern, and be structured in a way that is easy to read and understand.
- Test suite should have various helper function to make the arrange-act-assert pattern easy to follow and repeat across test cases. E.g. builder function, common assertions, etc.
- Test suite should focus on high-level functionality read -> manipulate -> write such that the implementation details can easily be changed without breaking tests, as long as the high-level functionality is preserved. So the arrange part should focus on creating input boards in markdown format, while the assert part should focus on comparing the output markdown with expected markdown.
- Whenever possible, test cases should use parameterization to cover multiple scenarios with the same test logic, to reduce code duplication and improve readability.


## Features
The API should allow users to easily make script that preform actions such as:

- Read and write Kanban board(s).
- Find tasks with specific tags or inline fields.
- Add, update, and remove tags and inline fields from tasks.
- Add, update, and remove tags and tags from tasks.
- Find lanes with specific names.
- Update line properties such as WIP limits, title, etc.
- Move tasks between lanes and boards.
- Loop through tasks in a lane or board.
- Loop through subtasks of a task.
- Add and remove tasks from lanes.
- Archive and unarchive tasks.
- Read, update, remove, and add frontmatter and settings.
