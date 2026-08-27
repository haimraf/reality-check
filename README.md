# Homepage Reality Check

An agent skill that diagnoses a homepage in one pass.

It answers one question: is this page a product people can understand and act on, or a polished demo?

## What you get

- One verdict (`ship`, `after 3 fixes`, or `do not ship`)
- Exactly three fixes, ranked by damage
- One to three locked elements that must not be redesigned

v1 covers the homepage / primary landing page only. It does not run SEO, security, accessibility, or visual redesign audits.

## Install

[Download the repository as a ZIP](https://github.com/haimraf/reality-check/archive/refs/heads/main.zip), extract it, and copy the `reality-check` folder into your agent's skills directory.

You can also clone or copy the repository manually. The skill folder contains `SKILL.md`, `metadata.json`, and `SKILL_HE.md`.

## Compatibility

Tested with Codex and Grok. Designed to work with Claude and other agents that support skill folders.

Triggers include "reality check", "bdikat metziut", and "ma shavur baamud harishon".

## License

MIT. Author: Studio Haim.
