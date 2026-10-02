# Step 2: Plan

Write `<output-dir>/promo-plan.md` with these sections, then stop for approval.

## 1. Angle per feature

One paragraph: the promise, who it's for, the tone (see `tones.md`), and why this angle beats the obvious one. Prefer the user's real situation ("rent day, without the panic") over the feature's name ("AI eye opener").

## 2. Hooks

`--hooks` variants per feature (default 3), each testing a **different idea**, not different wording:

| Hook type | Pattern | Example |
|---|---|---|
| Result first | Open on the after, then rewind to the before | Finished budget → "this was a shoebox of receipts" |
| Problem | Name the pain in the viewer's words | "When the only good photo has your eyes closed" |
| Demo | Start mid-action on the feature | Finger-free: the tap and the transform, immediately |
| Contrast | Split or swipe before/after | Before/after wipe with one line of text |
| Curiosity | A question or claim that needs the ad to answer | "Wait, it reads the receipt for you?" |

Each hook gets: the first-frame visual, on-screen text (≤ 7 words), and the 1.5-second payoff.

## 3. Storyboards

One table per format, durations summing to the target:

| # | Time | Visual (shot ID or asset) | On-screen text | Audio |
|---|---|---|---|---|

Starting shapes (adapt, don't copy):

- **Reel / feed / square, 15 s:** Hook (0–2 s) → Demo (2–9 s: the real feature, 2–3 beats) → Proof (9–12 s: before/after or second example) → End card (12–15 s: app name, icon, "Free on the App Store").
- **App Store preview, 20–28 s:** screen capture only. Strongest result frame settled at **5 s** (poster). Feature demo → second beat → other features briefly if the plan includes them → end on the app's main screen. Text overlays for each beat.
- **Screenshots:** one per feature or benefit, ordered by importance (the first two show in search results). Each: a short benefit caption (≤ 6 words) + the app in use, ideally the result state.

Square and feed versions reuse the reel's best hook with re-framed layout, not a crop.

## 4. Shot list

Every clip to record in step 3, with an ID, the screen, the action, the demo content, and the length needed (+1 s handles each side). Example: `S1 — Scanner, tap "Scan receipt", totals animate in — receipt demo-01.jpg — 5 s`.

## 5. Assets to generate

| Asset | Purpose | Model | Count | Est. cost |
|---|---|---|---|---|

Include demo photos (if generated), hook art, end-card background, music (1 bed per tone, ~30 s), voiceover lines, avatar clips. Run `scripts/fal_run.py check <endpoints>` for prices; if the unit is unclear, say so and give the count. Re-generations only for rejects.

## 6. Copy plan

Per feature: 3 primary texts, 3 headlines, 1 description, the CTA; Google App campaign headlines (≤30) and descriptions (≤90); TikTok ad text (≤100, no hashtags); App Store preview overlay lines; screenshot captions. Mark which grounded claim each line uses.

## 7. Music and voice

Mood, tempo (BPM), instruments, energy curve (where it lifts), and whether the end card gets a sting. Voiceover only with `--voice`: the lines, timed to the storyboard, never just reading the on-screen text.

## Reading-time floor

On-screen text needs ~0.3 s per word once fully visible, minimum 0.8 s. A 7-word hook needs ~2.1 s settled. If the storyboard can't fit it, cut words, not time.
