# Motion patterns

Pick screen 1 from the app's core transformation. Pick the rest from what the user needs to understand or decide. Two to four screens is usually right; every extra screen loses people.

## By app type

| App type | Screen 1 (the hook) | Good follow-ups |
|---|---|---|
| Photo / video editing | `DissolveHero`: before dissolves to after with a light sweep | `CompareSlider` with a hint wipe; `PermissionPrimer` (photos/camera) |
| Style / filter / avatar apps | `DissolveHero` cycling through 2–3 variants of one image (original → style A → style B), pill shows the current one | `ChoiceQuestion` (pick a style); `CompareSlider` |
| Video / filters | `LoopingVideo` of the effect, title over a dark fade | `CompareSlider` on a still |
| Fitness / health | `StatReveal`: ring fills, number counts up | `ChoiceQuestion` (goal, level); notifications primer |
| Finance / budgeting | `StatReveal` with a growing chart line or stacking cards via `ParallaxHero` | `ChoiceQuestion` (goal); security reassurance screen |
| Productivity / to-do | Messy list items springing into order (staggered `offset` + `opacity`) | `ChoiceQuestion` (use case); notifications primer |
| Language / education | Word flipping between languages (`contentTransition(.numericText)` or rotation), streak flame scaling | `ChoiceQuestion` (level, daily goal) |
| Meditation / sleep | Slow breathing gradient (`phaseAnimator` on scale + hue, 4–6 s) with particles | `ChoiceQuestion` (goal); notifications primer |
| AI chat / generator | Prompt typing in character by character, result fading up | Example gallery with `ParallaxHero` |
| Games | `ParallaxHero` with character and scene layers; tap gives a bounce + haptic | — |

## Timing that feels premium

- Entrances: `.smooth(duration: 0.7)` with 0.1–0.15 s stagger between elements (`reveal(_:delay:)` in the template).
- Ambient motion: slow, 5–8 s loops (`phaseAnimator`), small amplitudes (scale 1.0 → 1.06, drift a few points).
- The main event (dissolve, count-up): 1.2–1.5 s, eased, with 1.5–3 s holds on each state so the eye can read it.
- Secondary motion (sheen, sparkle, label change) happens *during* the main event, not on its own timer.
- Nothing bounces more than `bounce: 0.25`. Nothing blinks.

## Building blocks

- `KeyframeAnimator(initialValue:repeating:)` for multi-track loops that must stay in sync (dissolve + sheen).
- `PhaseAnimator` / `.phaseAnimator([a, b])` for simple ambient loops.
- `.contentTransition(.numericText())` for numbers, `.interpolate` for label text.
- `matchedGeometryEffect` to carry an element (a photo, a card) from one page into the next.
- `.sensoryFeedback` for haptics: light impact on page change, selection while dragging, success on finish.
- `.visualEffect { content, proxy in ... }` for scroll- or position-driven parallax without `GeometryReader` layout side effects.

## Reduce Motion

Every pattern needs a still that still tells the story: the dissolve shows the After frame, the slider sits at the middle, counters show the final number, parallax layers sit still.
