# Homepage Reality Check

An agent skill that diagnoses a homepage in one pass.

It answers one question: is this page a product people can understand and act on, or a polished demo?

## What you get

- One verdict (`ship`, `after 3 fixes`, or `do not ship`)
- Exactly three fixes, ranked by damage
- One to three locked elements that must not be redesigned

v1 covers the homepage / primary landing page only. It does not run SEO, security, accessibility, or visual redesign audits.

## Install

```bash
npx skills-il add https://github.com/haimraf/reality-check
```

This installs the skill directly from this GitHub repository. You can also copy the repo (or just `SKILL.md` + `metadata.json` + `SKILL_HE.md`) into your agent's skills directory as a folder named `reality-check`.

Triggers include "reality check", "bdikat metziut", and "ma shavur baamud harishon".

## License

MIT. Author: Studio Haim.
