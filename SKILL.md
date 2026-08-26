---
name: reality-check
description: Run a homepage Reality Check. Is this page a real product or a demo in costume? Returns one verdict, exactly three fixes ranked by damage, and what must not be touched. Use when the user asks to check a homepage, landing page, or site for clarity, fake-working components, generic claims, missing primary action, production readiness of the first screen, "reality check", "bdikat metziut", or "ma shavur baamud harishon". Do NOT use for full SEO, security, accessibility, or redesign audits.
license: MIT
compatibility: Needs live URL or pasted above-the-fold copy. Works with Claude Code, Claude.ai, Cursor.
metadata:
  version: "1.0.0"
  author: Studio Haim
  category: marketing-growth
  display_name:
    he: בדיקת מציאות לעמוד הבית
    en: Homepage Reality Check
  display_description:
    he: אבחון עמוד בית - מוצר אמיתי או דמו מלוטש. מחזיר פסק דין אחד, בדיוק 3 תיקונים לפי נזק, ומה לא לגעת בו. לא SEO, לא נגישות, לא רידיזיין.
    en: Diagnose a homepage - real product or polished demo. Returns one verdict, exactly three damage-ranked fixes, and what must not be touched. Not for SEO, accessibility, or redesign audits.
  tags:
    he:
      - בדיקת-אתר
      - עמוד-הבית
      - חוויית-משתמש
      - בהירות-מוצר
      - הנעה-לפעולה
      - וייב-קודינג
    en:
      - website-audit
      - homepage
      - ux
      - product-clarity
      - cta
      - vibe-coding
---
# Reality Check

A homepage diagnosis skill. It does not redesign. It does not invent business strategy.
It answers one question: **is this page a product people can understand and act on, or a polished demo?**

v1 scope is **homepage / primary landing page only**.

## Trigger

Activate when the user asks things like:

- "reality check on this site"
- "is this homepage clear"
- "does this page actually work"
- "בדיקת מציאות לעמוד הבית"
- "מה שבור בעמוד הראשון"
- check for AI slop, dead buttons, generic copy, missing CTA, fake proof

Do **not** activate for full-site SEO audits, security reviews, accessibility compliance, or visual redesign requests unless the user explicitly wants a Reality Check first.

## Scope (v1)

| In scope | Out of scope |
|----------|--------------|
| Homepage / main landing page | Interior pages (unless user forces one page) |
| What the product is | Brand strategy workshops |
| Primary action | Full funnel analytics |
| Proof vs claims | Security / RLS / secrets |
| Noise and duplication | Lighthouse performance scores |
| Dead / fake / disconnected UI | WCAG / IS 5568 full audit |
| | SEO technical crawl |

Hebrew quality, mobile layout, cookie banners, and AI-generic tone are **signals inside modules**, not separate modules. Only raise them if they break understanding, action, trust, or reality.

## Input

Prefer, in order:

1. Live URL of the homepage
2. If no URL: pasted hero + above-the-fold copy, or screenshots + nav labels
3. Optional: repo or builder context (Lovable / Bolt / v0 / Cursor) - use only as a hint for common failure patterns, never as proof

If the page cannot be read, say so and stop. Do not invent content.

## Pipeline

```
Page
  → 5 modules (candidate findings only)
  → internal findings pool
  → damage ranking
  → verdict
  → exactly 3 fixes
  → 1–3 locked elements
  → fixed output contract
```

Modules never write report chapters. They only emit **candidate findings**.
One decision layer picks what ships in the output.

---

## Module 1 — Name noun (שם עצם)

**Asks:** Within ~8 seconds, is it clear what this is, who it is for, and what is sold or built — with a concrete noun, not philosophy?

**Failure when:**
- No concrete noun for what is built/sold (only “solutions”, “growth”, “digital”, “excellence”)
- Audience is missing or pure buzzword
- Headline is pure approach/process with no catalog
- Name-swap test passes: replace the brand name with a competitor and the copy still works

**Allowed fix type:**
- Sharpen existing positioning line to include a concrete noun
- Point out that the catalog exists below the fold and must surface earlier
- **Not** invent a new product category the page never mentions

---

## Module 2 — Action (פעולה)

**Asks:** Is it clear what the user should do now, and is there one primary CTA that does not compete with itself?

**Failure when:**
- No clear primary CTA above the fold
- Two primary CTAs at equal strength
- Vague CTAs only (“learn more”, “discover”, “שלח/י” with no context)
- Primary path does not match what the page promises

**Allowed fix type:**
- Sharpen or prioritize an **action that already exists** on the page
- If multiple services exist and none is marked primary: say **“choose one primary business action”** — do **not** pick which service should win
- Reduce competing CTAs; do not add new buttons

**Hard rule:** Never invent a business goal the page does not support. Reality Check diagnoses; it does not become the client’s strategist.

---

## Module 3 — Proof (הוכחה)

**Asks:** Do the page’s claims rest on credible evidence, or do they float?

**Failure when:**
- Claims without evidence (numbers, live product, before/after, named process, real screenshot)
- “Proof” that looks generic or fabricated
- “Real / trusted / leading” labels with nothing behind them
- Contradictory claims across sections

**Allowed fix type:**
- Connect an existing claim to existing evidence on the page
- Remove or tone down a claim that has no support
- **Not** invent testimonials, metrics, or case studies

---

## Module 4 — Noise (רעש)

**Asks:** What competes for attention, duplicates the message, or can be deleted without harming understanding?

**Failure when:**
- Multiple primary messages at once
- Blocks that repeat the same idea
- Elements that pull focus from the primary action
- Content that can be removed and the page becomes clearer

**Allowed fix type:**
- Delete or shorten only
- Defer secondary paths lower
- **Not** add sections, not full reorder redesign

---

## Module 5 — Reality (מציאות)

**Asks:** Does anything look active or real but is actually dead, invented, disconnected, or self-contradicting?

**Failure when:**
- Button / form / link that looks live and does nothing
- Nav item to 404, same page, or placeholder
- “Working” component that is static theater
- Text, numbers, or logos that sound fabricated
- Copy promises a screen that does not exist

**Allowed fix type:**
- Connect, remove, or strip the false appearance of liveness
- **Not** build a new feature

**Separation from Proof:**
- Proof = claim without evidence
- Reality = UI/path that pretends to work or exist and does not
Keep them distinct. A weak claim is Proof. A dead button is Reality.

---

## Candidate findings → Damage ranking

Collect all module candidates. Rank by damage:

1. **Breaks understanding** — user does not know what this is
2. **Breaks action** — user does not know what to do
3. **Breaks trust** — looks fake, dead, or contradictory
4. **Noise** — only if it weakens 1–3

Select **exactly three** fixes.
If a module finds only mild weakness, it may contribute **zero** items to the final three.
Do not force every module to “find something.”

**One fix = one damage.**
Do not pack two distinct module findings into one numbered fix just to fit the triple.
Proof (claim without evidence) and Reality (UI that pretends to work) stay separate: pick the higher-damage one for a slot; leave the weaker out of the three if needed.
“Exactly three fixes” means three ranked problems — not five problems compressed into three lines.

---

## Verdict rules

One verdict only:

| Verdict | When |
|---------|------|
| **אפשר לעלות** | Understanding + action + trust hold; remaining issues are minor noise |
| **רק אחרי 3 תיקונים** | Fixable damage in understanding, action, or trust; page is not hopeless |
| **אסור לעלות** | Core understanding or trust is broken and not fixable by three tight edits (e.g. product is unclear and proof is theater and primary path is dead) |

No “maybe”. No “almost”. One line of reason after the verdict.

---

## Locked elements (“מה לא לגעת בו”)

Always output **1–3** elements that work and must not be touched.

Purpose: stop the agent (and the human) from turning diagnosis into redesign.

Prefer locking:
- A sharp headline that differentiates
- Real proof already on the page
- A clear catalog/list of concrete offerings
- Honest status labels
- A working primary contact path

If almost nothing is lockable, lock the least-damaging real asset and say why.

---

## Output contract (mandatory every run)

No extra chapters. No scores per module. No 40-finding dump.

```text
# Reality Check — [site name or URL]

## פסק דין
אפשר לעלות / רק אחרי 3 תיקונים / אסור לעלות

[One sentence why.]

## 3 התיקונים הראשונים
1. [What to fix] — [Why it hurts] — [How in one sentence, without inventing strategy]
2. ...
3. ...

## מה לא לגעת בו
- [Element] — [Why lock it]
(1–3 items)

## למה זה המצב
[2–4 lines. Central reason only. Not a tour of all modules.]
```

Language: direct, Hebrew when the page/user is Hebrew. No “מומלץ לשקול”. No therapy-speak.

---

## Hard prohibitions

1. **Do not invent facts** — no made-up metrics, customers, or features.
2. **Do not invent business goals** — do not choose which service is “the” product if the page does not; say the page must choose.
3. **Do not force every module to fail** — empty candidate list from a module is valid.
4. **Do not propose redesign** — no new sections, no layout overhaul, no “rethink the brand”.
5. **Do not exceed three fixes** — rank and cut. Do not compress multiple distinct damages into one fix line.
6. **Do not expand into SEO / security / accessibility / performance audits** unless a specific issue directly breaks understanding, action, trust, or reality on the homepage (example: cookie banner covering the only CTA).
7. **Do not add CTAs or product lines** the page does not already support.
8. **Do not write five module scores or five module chapters** in the user-facing output.
9. **Do not merge Proof and Reality** into one fix. A floating claim and a dead control are two findings; rank them and keep only the worse one if the triple is full.

---

## Example internal discipline (not user-facing)

After modules run, the decision layer may look like:

- Name noun: mild (generic positioning) → not in top 3
- Action: severe (no primary CTA) → fix #1
- Proof: severe (app claimed, never shown) → fix #2
- Noise: severe (same paragraph ×4) → fix #3
- Reality: mild (no clear dead control) → not in top 3

That is correct behavior.

When Proof and Reality both fire:

- Reality: severe (dead video that looks live) → fix #3
- Proof: moderate (“leading” + big number, weak on-page evidence) → **out of the three**

Do not write: “remove dead video and tone down leading claim” as one fix. Pick one.

---

## v1 boundary

This skill is **Reality Check**.
v1 is homepage-only.
Later versions may widen scope; do not widen silently inside v1.
