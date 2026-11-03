---
name: reality-check
description: >-
  Homepage Reality Check. Diagnoses whether a homepage or main landing page is
  a real product people can understand and act on, or a polished demo. Returns
  one verdict, exactly three fixes ranked by damage, and 1-3 elements not to
  touch, with every finding marked verified, observed, or assumed. Use when the
  user asks for a reality check of a homepage, landing page, or a site's first
  screen, asks whether it is clear or ready to go live, or points to dead
  buttons, fake or placeholder UI, generic AI copy, a missing or competing CTA,
  or unsupported claims. Hebrew triggers: "בדיקת מציאות", "מה שבור בעמוד
  הראשון", "האם אפשר לעלות לאוויר", "bdikat metziut", "ma shavur baamud
  harishon". Do NOT use for full SEO, security, accessibility, performance, or
  redesign audits, for interior pages, or for reality checks of plans, code, or
  claims that are not a web page.
license: MIT
compatibility: >-
  Needs a live URL, a screenshot, or pasted first-screen copy. No MCP server,
  scripts, or extra permissions. Clicking controls needs a browser tool;
  without one, behavior findings stay unverified.
---
# Reality Check

Diagnosis only: no redesign, no invented business strategy. One question: **is this page a product people can understand and act on, or a polished demo?**

Scope (v1): the homepage or primary landing page. Out of scope: interior pages (unless the user names one), brand strategy, funnel analytics, security, performance, WCAG or IS 5568, SEO crawls. For those requests, run only if the user explicitly wants a Reality Check first. Hebrew quality, mobile layout, cookie banners, and generic AI tone count only when they break understanding, action, trust, or reality (example: a cookie banner covering the only CTA).

## 1. Read the page, record what you can verify

Inputs, best first. Builder context (Lovable, Bolt, v0, Cursor) hints at common failures; it is never proof.

| Input | Establishes | Cannot establish |
|---|---|---|
| Live page, rendered and clicked (use a browser tool if available) | Copy, layout, whether clicked controls, links, and forms work | Anything not clicked |
| Live page, text fetch only | Copy and its order | The fold, layout, mobile, whether anything works |
| Screenshots plus nav labels | What is in the frame, layout, the fold at that size | Whether anything works, anything outside the frame |
| Pasted first-screen copy | Wording | Layout, the fold, whether anything works |

Tag every fix with its evidence:

- **[verified]** (HE [נבדק]): exercised in this run (loaded, clicked, followed, submitted) and the result was seen.
- **[observed]** (HE [נצפה]): visible in the material provided, not exercised. Enough for findings about what the page says or shows.
- **[assumed]** (HE [הנחה]): inferred, not seen or tested. Phrase it as a check: "Verify that ...".

Evidence rules:

- Saying a control, link, form, or widget is dead, broken, static, or leads nowhere needs [verified]; from a screenshot or pasted copy it is [assumed] at most. Visible signs (placeholder text, "Lorem ipsum", "Coming soon" on a live-looking control) are [observed].
- Numbers that stay the same across reloads do not prove a widget is static; a real daily total can hold still. [verified] needs the data source: values hard-coded in the HTML with no request behind them.
- Calling testimonials, logos, or numbers fabricated needs visible signs; otherwise [assumed].
- "Do not ship" needs at least one [verified] or [observed] finding, never assumptions alone.

Stop without diagnosing when the page cannot be read: unreachable URL, login wall, or only a client-rendered shell (empty root div, "enable JavaScript", a script bundle with no copy; common in Lovable, Bolt, and v0 builds). An empty shell is not an empty page. Use the stop output and ask for a rendered view, a screenshot, or the pasted copy. Never invent content.

## 2. Five modules: candidate findings only

Modules never write report chapters. A module may find nothing, and a mild finding may stay out of the three. Do not force every module to fail.

**Name noun (שם עצם).** Within about 8 seconds: what is it, for whom, and what is sold or built, as a concrete noun?
Fails: only abstractions ("solutions", "growth", "digital", "excellence"); missing or buzzword audience; headline is pure approach with no catalog; the name-swap test passes (a competitor's name fits the same copy).
Fix: sharpen the existing line with a concrete noun, or surface a catalog that exists lower on the page. No product category the page never mentions.

**Action (פעולה).** Is it clear what to do now, with one primary CTA that does not compete with itself?
Fails: no clear primary CTA on the first screen; two primary CTAs of equal weight; only vague CTAs ("learn more", "discover", "שלח/י" with no context); the primary path does not match the page's promise.
Fix: sharpen or prioritize an action that already exists, or cut competing CTAs. If several services exist and none is primary, say "choose one primary business action" and do not choose for the client.

**Proof (הוכחה).** Do the claims rest on credible evidence?
Fails: claims with no evidence (numbers, live product, before/after, named process, real screenshot); generic or fabricated-looking "proof"; "real", "trusted", or "leading" with nothing behind it; claims that contradict each other.
Fix: connect an existing claim to existing evidence, or remove or tone down the claim.

**Noise (רעש).** What competes for attention, repeats the message, or can go without loss?
Fails: several primary messages at once; blocks repeating one idea; elements pulling focus from the primary action; content whose removal makes the page clearer.
Fix: delete, shorten, or move secondary paths lower. No full reorder.

**Reality (מציאות).** Does anything look live or real but is dead, invented, disconnected, or self-contradicting?
Fails: a control, form, or link that looks live and does nothing; a nav item to a 404, the same page, or a placeholder; a "working" component that is static theater; text, numbers, or logos that read as fabricated; copy promising a screen that does not exist.
Fix: connect it, remove it, or strip the false appearance of liveness. No new feature.

Proof is a claim without evidence. Reality is UI or a path that pretends to work or exist. A weak claim is Proof; a dead button is Reality.

## 3. Decide

Rank candidates by damage: (1) breaks understanding, the user does not know what this is; (2) breaks action, the user does not know what to do; (3) breaks trust, it looks fake, dead, or contradictory; (4) noise, only when it weakens 1-3.

Select exactly three fixes: three ranked problems, not five compressed into three lines. When Proof and Reality compete for a slot, keep the higher-damage one and leave the other out.

| Verdict (EN / HE) | When |
|---|---|
| Ship / אפשר לעלות | Understanding, action, and trust hold; what remains is minor |
| Only after 3 fixes / רק אחרי 3 תיקונים | Fixable damage to understanding, action, or trust |
| Do not ship / אסור לעלות | Core understanding or trust is broken beyond three tight edits (example: product unclear, proof is theater, and the primary path is dead) |

One verdict, no "maybe", no "almost". Under Ship only, a slot with no real finding left reads "No further fix needed." (HE: "אין תיקון נוסף שמצדיק עבודה."). Never invent a problem to fill a slot.

Lock 1-3 elements that work, so diagnosis does not turn into redesign: a sharp differentiating headline, real proof already on the page, a clear catalog of concrete offerings, honest status labels, or a primary contact path. Call it working only if verified. If almost nothing qualifies, lock the least damaging real asset and say why.

## 4. Output contract (every run)

Write in the user's language; quote page copy in its original language. No other sections, no module scores, no finding dumps.

```text
# Reality Check - [site name or URL]
Basis: [live page, interacted | live page, read only | screenshot | pasted copy]; not checked: [what]

## Verdict
[Ship | Only after 3 fixes | Do not ship]

[One sentence why.]

## Top 3 fixes
1. [evidence tag] [What to fix] - [Why it hurts] - [How, in one sentence, without inventing strategy]
2. ...
3. ...

## Do not touch
- [Element] - [Why lock it]

## Why
[2-4 lines. The central reason only, not a tour of the modules.]
```

Hebrew labels: `בסיס:` (אתר חי, נבדק בלחיצות | אתר חי, קריאה בלבד | צילום מסך | טקסט מודבק) and `לא נבדק:`, `## פסק דין`, `## 3 התיקונים הראשונים`, `## מה לא לגעת בו`, `## למה זה המצב`.

Stop output (HE: `לא אובחן:`):

```text
# Reality Check - [URL]
Basis: [what was received]
Not diagnosed: [why the page could not be read]. Send [a screenshot, the rendered page, or the pasted first-screen copy].
```

Tone: direct. No "consider", no "מומלץ לשקול", no therapy-speak.

## Hard rules

1. Do not invent facts: no made-up metrics, customers, testimonials, case studies, features, or page content.
2. Do not invent business goals or pick the primary service; say the page must choose.
3. Do not redesign: no new sections, layout overhaul, CTAs, product lines, features, or "rethink the brand".
4. Exactly three fixes, one damage each; Proof and Reality never share a fix.
5. Do not state unverified behavior as fact; tag it [assumed].
6. Do not expand into SEO, security, accessibility, or performance audits unless an issue directly breaks understanding, action, trust, or reality on the homepage.
7. Do not widen v1 scope silently. v1 is homepage only.

## Decision example (internal, not user-facing)

- Name noun: mild (generic positioning) -> not in top 3
- Action: severe (no primary CTA) -> fix 1
- Proof: severe (app claimed, never shown) -> fix 2
- Noise: severe (same paragraph x4) -> fix 3
- Reality: nothing found -> not in top 3

When both fire: Reality severe (a video that looks live, verified dead) -> fix 3; Proof moderate ("leading" plus a big number, weak evidence) -> out. Never "remove the dead video and tone down the leading claim" as one fix. Pick one.
