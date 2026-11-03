# Changelog

All notable changes to the Reality Check skill. Versions follow [Semantic Versioning](https://semver.org/). A version is released when its `v` tag is pushed; the release workflow then attests `SKILL.md`, `SKILL_HE.md`, and `metadata.json`.

## [1.1.0] - 2026-11-03

Same core: one verdict, exactly three damage-ranked fixes, 1-3 locked elements.

### Added

- Evidence tag on every fix: `[verified]` (exercised in this run), `[observed]` (visible, not exercised), `[assumed]` (inferred, phrased as a check). Hebrew: `[נבדק]`, `[נצפה]`, `[הנחה]`.
- A `Basis:` line under the title naming the input (live page interacted or read only, screenshot, pasted copy) and what was not checked.
- A table of what each input can and cannot establish.
- A defined stop output (`Not diagnosed:` / `לא אובחן:`) for pages that cannot be read, including client-rendered shells that a text fetch returns empty.
- English output labels (`Ship`, `Only after 3 fixes`, `Do not ship`, and section headings) next to the Hebrew ones.
- Hebrew-script triggers in the description, plus "ready to go live" / "האם אפשר לעלות לאוויר".
- `README.he.md`, a Hebrew README.
- Regression harness in `tests/`: package checks, an output checker, five cases with real inputs and reference outputs, counterexamples that must be rejected, and a trigger eval set. CI runs it on every pull request.
- The output checker accepts a hyphen, en dash, or em dash between the parts of a fix, requires the `not checked:` clause on report Basis lines, ignores denied or conditional phrases in its wording warnings, and reports a case that needs a browser as `BLOCKED` (never a pass) when the agent could not load or click the page. It also accepts the skill's input-table name for each input on the Basis line (for example "live page, text fetch only" for "live page, read only"). Unit tests cover each of these.

### Changed

- Claims that a control is dead, static, or leads nowhere need `[verified]`. From a screenshot or pasted copy they are `[assumed]`.
- `Do not ship` can no longer rest on assumptions alone.
- Numbers that stay the same across reloads no longer count as proof that a widget is static; `[verified]` needs the data source.
- Under `Ship` only, an empty slot reads "No further fix needed." instead of a problem invented to reach three.
- Output follows the user's language; page copy is quoted in its original language.
- A locked element is called working only if it was verified.
- Repeated rules are stated once. The `SKILL.md` body went from 1,646 to 1,511 words (9,888 to 9,140 bytes) while adding the rules above.
- The trigger list was removed from the body; only the frontmatter description affects activation.
- New negative triggers: performance audits, interior pages, and reality checks of plans, code, or claims that are not a web page.
- `SKILL_HE.md` is a full translation with the same sections, instead of a summary.
- `metadata.json`: `landing-page` tag, display descriptions mention the evidence tags.

### Fixed

- The root copy of the skill had drifted from `reality-check/` (old compatibility line, missing `grok`). Both copies are now identical, and CI fails if they differ.
- The root `SKILL.md` frontmatter carried a nested `metadata` block. The Agent Skills spec allows only string values there, and Claude Desktop rejects the key. That data lives in `metadata.json`.

## [1.0.0] - 2026-08-26

First public package: five diagnostic modules (name noun, action, proof, noise, reality), damage ranking, one verdict, exactly three fixes, 1-3 locked elements, Hebrew companion file, bilingual `metadata.json`.
