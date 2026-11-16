---
layout: page
title: Claude Code mods
description: context-bar and lens — two mods that put context, usage and activity next to the chat.
img: assets/img/projects/claude-mods.svg
importance: 2
category: claude
github: https://github.com/kakwok/claude-mods
---

Two [Claude Code mods](https://code.claude.com/docs/en/plugins/mods/overview) that make a long
session easier to read. Needs Claude Code v2.1.287 or later.

**[▶ Try the interactive demo](https://kakwok.github.io/claude-mods/)** to see both in colour with sample data.

### context-bar

A band above the prompt.

- How full the context window is, by category (like `/context`).
- Your 5-hour and weekly plan usage, with reset times.
- The model, with the band's frame in that model family's colour, so a wrong model stands out.
- After each turn, how much context the turn added: blue, amber from 5k, red from 20k.

### lens

A pane beside the chat with three tabs.

- **Activity**: files changed (the last turn's marked `●`), commands with pass/fail, recent tool calls.
- **Agents**: the plan checklist, subagents, and a timeline of what each one did.
- **Context**: what Claude Code added to the prompt, memory files, MCP servers and skills.

### Install

```
/plugin install context-bar --marketplace kakwok/claude-mods
/plugin install lens --marketplace kakwok/claude-mods
```

[Source on GitHub](https://github.com/kakwok/claude-mods) · [Interactive demo](https://kakwok.github.io/claude-mods/)
