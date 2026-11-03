# Homepage Reality Check

An agent skill that diagnoses a homepage in one pass. It answers one question: is this page a product people can understand and act on, or a polished demo?

[עברית](README.he.md)

## What you get

- **One verdict:** `Ship`, `Only after 3 fixes`, or `Do not ship` (in Hebrew: `אפשר לעלות`, `רק אחרי 3 תיקונים`, `אסור לעלות`).
- **Exactly three fixes,** ranked by damage: first what breaks understanding, then action, then trust.
- **One to three locked elements** that work and must not be redesigned.
- **An evidence tag on every fix,** so you know what was checked and what was inferred:

| Tag | Meaning |
|---|---|
| `[verified]` / `[נבדק]` | Exercised in this run: loaded, clicked, followed, submitted |
| `[observed]` / `[נצפה]` | Visible in what you provided, not exercised |
| `[assumed]` / `[הנחה]` | Inferred. Written as a check for you to run: "Verify that ..." |

It covers the homepage or primary landing page only. It does not run SEO, security, accessibility, performance, or redesign audits, and it never invents metrics, testimonials, features, or which service your business should lead with.

## Example

Given a screenshot of a homepage ([case 03](tests/cases/03-en-dead-controls-screenshot)), the skill cannot click anything, so it says so:

```text
# Reality Check - Shiftly (screenshot)
Basis: screenshot; not checked: whether any button, link, or panel works

## Verdict
Only after 3 fixes

The product and the primary action are clear on screen, but the main proof floats and the parts that must work could not be tested from a screenshot.

## Top 3 fixes
1. [assumed] Verify that "Start free trial" opens a working signup - it is the only primary action, so if it leads nowhere the page fails at the moment of intent - click it on the live site; connect it or remove it.
2. [observed] "Trusted by 10,000+ restaurants" stands alone, with no names, logos, or source behind it - an unsupported claim under the CTA reads as filler and weakens the page around it - connect it to evidence already on the page or tone it down.
3. [assumed] Verify that the "LIVE ACROSS SHIFTLY" panel shows real data - a panel labelled live with fixed numbers would be static theater - check where the numbers come from on the live site; if "1,284 shifts filled today" is hard-coded with nothing loading it, connect it to real data or drop the LIVE label.

## Do not touch
- "Shift scheduling for restaurants" - a concrete noun and a concrete audience in four words
- The three "How it works" steps - a named process that shows how the product is used

## Why
On screen the page does its job: it names the product, the audience, and one primary action.
A screenshot cannot show whether that action and the live panel are real, so the verdict holds until both are checked on the live site.
```

The same page checked live with a browser tool ([case 02](tests/cases/02-en-dead-controls-live/expected.md)) turns both assumptions into `[verified]` findings: the trial button only appends `#` to the URL, and the panel's numbers are hard-coded in the HTML with no data request behind them. More reference outputs, in English and Hebrew, are in [`tests/cases`](tests/cases).

## What to give it

| Input | What it can establish |
|---|---|
| Live URL, with a browser tool | Copy, layout, and whether the controls it clicked actually work |
| Live URL, text fetch only | Copy and its order. Not the layout, the fold, or whether anything works |
| Screenshot (plus nav labels) | What is in the frame and how it is laid out. Not whether anything works |
| Pasted first-screen copy | Wording only |

A live URL with a browser tool gives the strongest result. If a fetch returns only a JavaScript shell (common for Lovable, Bolt, and v0 builds), the skill stops and asks for a screenshot or the rendered page instead of judging an empty page.

## Triggers

The agent decides when to use the skill from its description. It responds to requests such as:

- English: "reality check this homepage", "is this landing page ready to go live", "is this homepage clear", "check the first screen for dead buttons, generic AI copy, or a missing CTA"
- Hebrew: "בדיקת מציאות", "מה שבור בעמוד הראשון", "האם אפשר לעלות לאוויר"
- Transliterated Hebrew: "bdikat metziut", "ma shavur baamud harishon"

It is not meant for SEO, security, accessibility, performance, or redesign audits, for interior pages, or for "reality checks" of business plans, code, or claims that are not a web page.

## Install

**From MCPRush** ([listing](https://mcprush.com/haimraf/reality-check)), with the [MCPRush CLI](https://github.com/mcprush/mcprush-cli):

```bash
npx mcprush@latest skill add haimraf/reality-check
```

That writes the skill into the current project for Claude Code. Add `--client <id>` for another agent and `--global` for your home directory.

**From GitHub:** [download the repository as a ZIP](https://github.com/haimraf/reality-check/archive/refs/heads/main.zip), extract it, and copy the `reality-check` folder (not the whole repository) into your agent's skills folder, for example `.claude/skills/` for Claude Code. The folder must stay named `reality-check`, because the name in `SKILL.md` has to match it.

For Claude Desktop or claude.ai, zip the `reality-check` folder and upload it as a skill.

## Compatibility

- Follows the [Agent Skills](https://github.com/agentskills/agentskills) format and passes its `skills-ref` validator.
- No MCP server, no scripts, no extra permissions. Clicking controls needs a browser tool; without one, behavior findings stay `[observed]` or `[assumed]`.
- Version 1.0.0 was tested with Codex and Grok. Version 1.1.0 passes the repository checks but has not yet been run through the regression cases in any agent.

## Repository layout

| Path | What it is |
|---|---|
| `reality-check/` | The installable skill: `SKILL.md` (what the agent loads), `SKILL_HE.md` (full Hebrew translation), `metadata.json` (directory metadata) |
| `SKILL.md`, `SKILL_HE.md`, `metadata.json` | Identical copies at the root for directories that read the repository root. Edit `reality-check/`, then copy the three files up. CI fails if they differ |
| `tests/` | Package checks, output checker, regression cases, trigger eval set |
| `CHANGELOG.md` | What changed in each version |

## Testing

All checks use only the Python standard library:

```bash
python3 tests/check_package.py
```

```bash
python3 tests/check_output.py --all
```

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

`check_package.py` verifies that both copies are identical, the frontmatter is flat and within limits, triggers and labels agree across the skill, its Hebrew translation, and both READMEs, the core rules are still present, and the `SKILL.md` body stays within its size budget. `check_output.py --all` checks every case folder: `expected.md` and `alt-*.md` (other valid answers) must pass with no warnings, `counterexample-*.md` must fail, and `blocked-*.md` must come out BLOCKED. The unit tests cover the checker's own edge cases.

To run a case against a real agent, give it the case's prompt and input (see `case.json` in each folder), save the answer, and check it:

```bash
python3 tests/check_output.py answer.md --case tests/cases/03-en-dead-controls-screenshot
```

The result is `PASS` (exit 0), `FAIL` (exit 1, a contract break or a mechanical case expectation), or `BLOCKED` (exit 2). `BLOCKED` means the case needs a live interaction the agent's environment could not provide, such as case 02 without a browser that can reach the local server. It never counts as a pass. `WARN` lines are wording worth a human look. Fix separators may be a hyphen, en dash, or em dash. `tests/triggers.json` lists prompts that should and should not activate the skill; run them by hand in each agent, since activation depends on the agent.

## License

MIT. Author: Studio Haim.
