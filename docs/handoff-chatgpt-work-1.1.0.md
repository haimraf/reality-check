# Handoff to ChatGPT Work: Reality Check 1.1.0

<div dir="rtl">

## בקצרה

- **מה מוכן:** גרסה 1.1.0 של Reality Check נמצאת ב-[PR #2](https://github.com/haimraf/reality-check/pull/2), בענף `claude/great-clarke-3bujss`. ה-PR פתוח ולא מוזג.
- **מקור האמת:** GitHub. כל ערך שמופיע ב-MCPRush צריך להגיע מהקבצים במאגר, לא להיכתב מחדש ביד.
- **מה צריך אישור של חיים לפני ביצוע:** מיזוג ל-main, תגית `v1.1.0`, GitHub Release, ועדכון הדף ב-MCPRush Studio.
- **מה לא נבדק עדיין:** הגרסה החדשה לא הורצה ב-Codex או ב-Grok. הדף הנוכחי ב-MCPRush לא נבדק, כי mcprush.com היה חסום בסביבה שבה הוכנו השינויים, ולכן שמות השדות בסעיף 6 הם הצעה שצריך להתאים למה שמופיע ב-Studio בפועל.

</div>

## 1. Status

| Item | State |
|---|---|
| Pull request | [haimraf/reality-check#2](https://github.com/haimraf/reality-check/pull/2), open, not merged |
| Branch | `claude/great-clarke-3bujss`, based on `main` at `e015e42` |
| CI | `.github/workflows/validate.yml` (new) runs on the PR |
| Released version | `1.0.0` (tag `v1.0.0`) |
| Target version | `1.1.0`, in `metadata.json` and `CHANGELOG.md`, marked Unreleased |
| Tag `v1.1.0` | Not created. Needs Haim's approval |
| GitHub Release | Not created. Needs Haim's approval |
| MCPRush listing | Not touched. [Listing](https://mcprush.com/haimraf/reality-check), current contents not inspected |

## 2. Source of truth

- Repository: https://github.com/haimraf/reality-check
- Installable skill folder: `reality-check/` with `SKILL.md`, `SKILL_HE.md`, and `metadata.json`.
- The same three files sit at the repository root as byte-identical copies, for directories that read the root. CI fails if they differ. Edit `reality-check/` first, then copy the files up.
- Field values for MCPRush come from `reality-check/metadata.json` (names, descriptions, tags, version) and the `SKILL.md` frontmatter (description, compatibility).

## 3. Files changed in PR #2

| File | Change |
|---|---|
| `reality-check/SKILL.md` and root `SKILL.md` | 1.1.0 instructions: evidence tags, basis line, input table, stop output, English and Hebrew labels, Hebrew triggers in the description, rules deduplicated. Root copy no longer has the nested `metadata` block |
| `reality-check/SKILL_HE.md` and root copy | Full Hebrew translation with the same sections (was a summary) |
| `reality-check/metadata.json` and root copy | `version` 1.1.0, `landing-page` / `דף-נחיתה` tag, display descriptions mention evidence tags, `grok` in `supported_agents` at the root too |
| `README.md` | Rewritten: real example output, input table, triggers, install, compatibility, testing |
| `README.he.md` | New Hebrew README |
| `CHANGELOG.md` | New: 1.1.0 (Unreleased) and 1.0.0 |
| `tests/check_package.py` | New package checks (standard library only) |
| `tests/check_output.py` | New output contract checker (standard library only) |
| `tests/contract.json` | Output labels, rule anchors, size budget |
| `tests/triggers.json` | Canonical triggers and the activation eval prompts |
| `tests/cases/01` to `05` | Regression inputs, reference outputs, counterexamples |
| `tests/render_screenshot.js` | Regenerates the case 03 screenshot |
| `.github/workflows/validate.yml` | New CI, read-only permissions |
| `.gitignore` | New: Python bytecode, `node_modules/` |
| `docs/handoff-chatgpt-work-1.1.0.md` | This file |

## 4. Target version

`1.1.0`. It is a minor version: the output gains a `Basis:` line and an evidence tag on each fix, but the structure stays the same (one verdict, three fixes, 1-3 locked elements, one "why" section). Nothing a user relied on was removed.

## 5. Triggers

The agent decides activation from the `SKILL.md` description alone. Exact value (one line, 861 characters, 907 UTF-8 bytes):

```text
Homepage Reality Check. Diagnoses whether a homepage or main landing page is a real product people can understand and act on, or a polished demo. Returns one verdict, exactly three fixes ranked by damage, and 1-3 elements not to touch, with every finding marked verified, observed, or assumed. Use when the user asks for a reality check of a homepage, landing page, or a site's first screen, asks whether it is clear or ready to go live, or points to dead buttons, fake or placeholder UI, generic AI copy, a missing or competing CTA, or unsupported claims. Hebrew triggers: "בדיקת מציאות", "מה שבור בעמוד הראשון", "האם אפשר לעלות לאוויר", "bdikat metziut", "ma shavur baamud harishon". Do NOT use for full SEO, security, accessibility, performance, or redesign audits, for interior pages, or for reality checks of plans, code, or claims that are not a web page.
```

Canonical lists (from `tests/triggers.json`):

| Kind | Phrases |
|---|---|
| English | reality check, homepage, landing page, first screen, ready to go live, dead buttons, generic AI copy, CTA |
| Hebrew | בדיקת מציאות · מה שבור בעמוד הראשון · האם אפשר לעלות לאוויר |
| Transliterated | bdikat metziut, ma shavur baamud harishon |
| Not for | SEO, security, accessibility, performance, redesign, interior pages, reality checks of plans, code, or claims |

Example prompts suitable for a listing page (all from `tests/triggers.json`):

- Run a reality check on https://shiftly.example
- Is our homepage ready to go live?
- Does this landing page actually work, or is it just a pretty demo?
- תעשה בדיקת מציאות לעמוד הבית שלנו
- האם אפשר לעלות לאוויר עם דף הנחיתה הזה?

## 6. MCPRush Studio: what to update

Field names below are descriptive. Match each to the field Studio actually shows, and copy values from the files rather than from this table when they differ.

| Field | Value | Source |
|---|---|---|
| Slug / name | `reality-check` (keep; changing it breaks existing installs) | `SKILL.md` `name` |
| Title (EN) | Homepage Reality Check | `metadata.json` `display_name.en` |
| Title (HE), if supported | בדיקת מציאות לעמוד הבית | `metadata.json` `display_name.he` |
| Short description (EN) | Diagnose a homepage: real product or polished demo. Returns one verdict, exactly three damage-ranked fixes, and what must not be touched, with each finding marked verified, observed, or assumed. Not for SEO, accessibility, or redesign audits. | `metadata.json` `display_description.en` |
| Short description (HE), if supported | אבחון עמוד בית: מוצר אמיתי או דמו מלוטש. מחזיר פסק דין אחד, בדיוק 3 תיקונים לפי נזק, ומה לא לגעת בו, וכל ממצא מסומן נבדק, נצפה או הנחה. לא SEO, לא נגישות, לא רידיזיין. | `metadata.json` `display_description.he` |
| Long description / readme | The "What you get", "Example", and "What to give it" sections of `README.md` | `README.md` |
| Version | 1.1.0, only after the merge and the `v1.1.0` tag | `metadata.json` `version` |
| Changelog / release notes | The 1.1.0 entry of `CHANGELOG.md` | `CHANGELOG.md` |
| Tags | website-audit, homepage, landing-page, ux, product-clarity, cta, vibe-coding | `metadata.json` `tags.en` |
| Category | Closest match to `marketing-growth` in MCPRush's own category list | `metadata.json` `category` |
| Source repository | https://github.com/haimraf/reality-check | |
| Source path, if Studio asks | `reality-check/`. If it reads the repository root, that also works: the root copy is identical. With `reality-check/` the installed folder holds only the three skill files, without `tests/` and `docs/` | |
| Branch or ref | `main` after the merge, or the `v1.1.0` tag if Studio pins a ref | |
| Required tools, permissions, MCP servers, env vars | None | `SKILL.md` `compatibility` |
| Compatibility note | Needs a live URL, a screenshot, or pasted first-screen copy. No MCP server, scripts, or extra permissions. Clicking controls needs a browser tool; without one, behavior findings stay unverified. | `SKILL.md` `compatibility` |
| Supported clients | claude-code, cursor, github-copilot, windsurf, opencode, codex, gemini-cli, grok | `metadata.json` `supported_agents` |
| Tested clients | 1.0.0: Codex, Grok. 1.1.0: cases 01-05 passed in one blind run in ChatGPT Work (Codex-based agents) on 2026-11-03; not run in Grok, Codex CLI, or Codex cloud | `README.md` |
| Install command | `npx mcprush@latest skill add haimraf/reality-check` | MCPRush CLI README |
| Example output | Case 03 output in `README.md` (screenshot input, shows `[assumed]` tags) | `tests/cases/03-en-dead-controls-screenshot/expected.md` |
| Price / plan | No change from the current listing. This PR does not touch pricing | |

## 7. Release sequence

Each step needs Haim's explicit approval before it is taken.

1. Run cases 01-05 in Codex and Grok (README, section Testing). Save each answer and check it with `python3 tests/check_output.py answer.md --case tests/cases/<case>`. Record the results on PR #2. A `BLOCKED` result (case 02 without a browser that can reach the local server) is not a pass: rerun it where a browser works.
2. Merge PR #2 into `main` through GitHub, with CI green.
3. Create tag `v1.1.0` on `main`. The existing `release.yml` attests `SKILL.md`, `SKILL_HE.md`, and `metadata.json`.
4. Optionally publish a GitHub Release from that tag, using the 1.1.0 changelog entry. Change `## [1.1.0] - Unreleased` to the release date in a follow-up commit.
5. Update MCPRush Studio with the values in section 6.

## 8. Checks after the MCPRush update

- `npx mcprush@latest skill add haimraf/reality-check --dry-run` lists the files it would write. Expect `SKILL.md`, `SKILL_HE.md`, and `metadata.json`, plus the rest of the repository if the listing reads the root.
- In the written folder, `metadata.json` shows `"version": "1.1.0"`, and the first lines of `SKILL.md` show `name: reality-check` and the description in section 5.
- The listing page shows the 1.1.0 description and version, and the install command it prints is `haimraf/reality-check`.
- One trigger test in an installed agent: "תעשה בדיקת מציאות לעמוד הבית שלנו" should activate the skill and produce a `בסיס:` line.

## 9. Open items and risks

- **One agent run so far.** Cases 01-05 passed once in ChatGPT Work on 19f49f7. The reference outputs in `tests/cases` were written by hand from the rules; `alt-text-fetch-only.md` in case 04 is the one recorded agent output kept in the repo.
- **Name collision.** Other publishers have skills named `reality-check` (for code and claims, not homepages). Two skills with the same folder name cannot sit side by side in one skills folder. The description now separates them by scope. Renaming would be a breaking change and is Haim's call.
- **`compatibility` in Claude Desktop uploads.** The Agent Skills spec allows it, and 1.0.0 already had it in `reality-check/SKILL.md`. Whether Claude Desktop's upload accepts it was not verified.
- **Skills IL.** If Skills IL reads the repository root as the skill folder, its validator would flag the root `README.md` ("no README in a skill folder") and expects sections such as Examples and Troubleshooting. Not addressed in this PR; MCPRush was the target.
- **MCPRush taxonomy unknown.** Category and tag fields depend on what Studio offers.

## 10. Do not

- Do not merge, tag, release, or publish anything on MCPRush without Haim's explicit approval.
- Do not edit the root `SKILL.md`, `SKILL_HE.md`, or `metadata.json` on their own. Change `reality-check/` and copy them up.
- Do not put a `metadata:` block back into `SKILL.md` frontmatter; enriched metadata belongs in `metadata.json`.
- Do not widen the skill into SEO, security, accessibility, performance, or redesign audits.
