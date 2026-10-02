---
name: onboard
description: Build an animated, interactive onboarding flow for an iOS app in SwiftUI, with brand-matched art generated on fal (GPT Image 2.5), then build it and check every screen in the iOS Simulator. Works for SwiftUI and UIKit apps, new or replacing an existing intro. Use when the user asks to make, redesign, animate or improve onboarding, intro, welcome or walkthrough screens for an iOS app, or wants art generated for them.
---

# /onboard

Turn an iOS app into a short, animated onboarding that sells the app in its first seconds: real motion, real interaction, art that looks like it belongs to the brand. The output is SwiftUI source wired into the app, assets in its asset catalog, and screenshots proving each screen works.

Arguments (all optional): a path to the Xcode project, the number of screens, a style (`glossy product-ad`, `soft 3D clay`, `flat pastel vector`, `editorial photo`, `dark premium`, `playful`, or the name of an app whose look to borrow), and `--no-art` to build with existing images and SF Symbols only.

## Requirements

- macOS with Xcode and an iOS Simulator runtime that meets the app's deployment target. The templates need **iOS 17+** (`KeyframeAnimator`, `PhaseAnimator`, `sensoryFeedback`). For an older target, guard them with `if #available(iOS 17, *)` and show the still version below that.
- `FAL_KEY` in the environment for art generation. Never ask the user to paste a key into the chat, never print it, never write it into a file. If it is missing, give them a command that reads it without echoing (`read -s`) and appends to their shell profile (check `$SHELL`: `~/.zshrc` for zsh, `~/.bash_profile` for bash).
- Python 3. Pillow is optional (used by `pair_check.py` and `contact_sheet.py`).

Scripts live in this skill's `scripts/` folder, templates in `templates/`, deeper guidance in `references/`. Read a reference when its step comes up, not all up front.

## Step 1: Inspect the app

Read [references/inspect.md](references/inspect.md), then answer these before planning, in writing:

1. **What is it, in one sentence?** Use the app's own words (App Store copy, `Info.plist` display name, README, strings files).
2. **What is the single moment that makes someone want it?** For a photo editor that is the before/after; for a habit app, the streak; for finance, money growing. This becomes screen 1.
3. **Brand:** accent and background colors (hex), fonts, light or dark, existing icon and imagery.
4. **Architecture:** SwiftUI `App` or UIKit (`AppDelegate`/`SceneDelegate`/storyboard)? Deployment target? Is there an existing onboarding, and what flag marks it complete? Is there a paywall (RevenueCat, StoreKit, Adapty, Superwall) the last screen should hand off to?
5. **Permissions** the app requests early (camera, photos, notifications, tracking): each deserves a primer screen before the system prompt.

## Step 2: Plan, and get approval before spending credits

Write `onboarding-plan.md` in the app's repo (or the scratchpad if the user doesn't want it committed):

- Screen by screen: purpose, headline and subline (short, specific, in the app's voice), the motion pattern from [references/motion-patterns.md](references/motion-patterns.md), interaction, CTA label.
- An asset table: name, what it shows, model, size, background, and which asset it derives from (for edit pairs).
- One **style lock**: a shared paragraph of art direction (lighting, palette with the brand hex, lens or render style, background) that every prompt includes. This is what makes the set look like one campaign.
- The cost estimate from `scripts/fal_gen.py check`.

Show the plan and stop. Generate nothing until the user approves. If they asked for a specific number of screens, build exactly that many.

## Step 3: Generate the art

Read [references/art-direction.md](references/art-direction.md). The core rules:

- **Confirm model IDs first** (`scripts/fal_gen.py models gpt-image`). Defaults: `openai/gpt-image-2.5/flare/text-to-image` and `openai/gpt-image-2.5/flare/edit`.
- **Generate the hero alone first**, look at it, and show the user. Only then generate the rest, in parallel.
- **Pairs come from edits, never two separate generations.** Generate one image, then derive the other with the edit model, changing only the one thing the app changes. Then run `scripts/pair_check.py`: the difference outside the edited region must be small (under about 4 on a 0–255 scale), or the dissolve and slider will show the face shifting.
- **Look at every image** before using it. Reject and regenerate only the failures, with a corrected prompt.
- **Honesty:** a generated before/after implies "the app does this". Label it "Illustrative example" on screen and tell the user to swap in real app output before shipping, since App Review rejects misleading claims about what an app does. Generated art is fine for everything that isn't a claim about results.
- Add finished images with `scripts/add_to_assets.py` (JPEG for photos, PNG for transparency), prefixed `onb-` so they're easy to find and remove.

Keep the prompts in `tools/prompts/` (or next to the plan) so any image can be regenerated.

## Step 4: Build the screens

Start from the templates; copy them into the app and rename to its brand. Do not add them as a package.

| Template | Use |
|---|---|
| `templates/OnboardingFlow.swift` | Container: paged `TabView`, page dots, CTA, `reveal` entrance modifier, debug start page, completion flag. Always used. |
| `templates/DissolveHero.swift` | Self-playing before/after: dissolve with a synced light sweep and a Before/After pill. Best screen 1 for any "transform" app. |
| `templates/CompareSlider.swift` | Drag-to-compare with an auto hint wipe, haptics, VoiceOver adjustable action. |
| `templates/ParallaxHero.swift` | Layered art drifting at different depths, plus drag parallax. For illustration-led apps. |
| `templates/StatReveal.swift` | Counting number + filling ring. Fitness, finance, habits, productivity. |
| `templates/ChoiceQuestion.swift` | Personalization question with animated cards, saved to `@AppStorage`. |
| `templates/PermissionPrimer.swift` | Explains why, then triggers the real camera / photos / notifications prompt. |
| `templates/LoopingVideo.swift` | Muted looping HEVC clip as a background (from image-to-video). |
| `templates/UIKitHosting.swift` | Presenting the SwiftUI flow from a UIKit app. |

Rules that came from real bugs, so follow them:

- **Pages inside a paged `TabView` don't get `onAppear` reliably.** Pass `isActive: index == n` and start animations in `.onChange(of: isActive, initial: true)`.
- **The pager itself must ignore the safe area** (`TabView { ... }.ignoresSafeArea()`, as in `OnboardingFlow`). If it doesn't, the pager stops at the status bar and full-bleed pages show a black strip above the photo, even though each page ignores the safe area. Keep this when putting pages into an existing container.
- **Full-bleed pages** use `.ignoresSafeArea(edges: .top)`, and then anything pinned near the top (labels, pills) must be offset by the real window inset (see `topInset` in the template), or it lands under the clock and the Dynamic Island.
- **Keyframe-driven values must not inherit a parent animation.** If a parent has a slow zoom (`phaseAnimator`), put `.transaction { $0.animation = nil }` on the keyframed layers, or the parent's 7-second curve smears a 1-second dissolve and labels fall out of sync.
- **Decorative layers go in `.overlay`, not as `ZStack` siblings.** An oversized sheen in a `ZStack` changes the layout and pushes the photo.
- **Auto-playing reveals should not use a hard divider line.** A dissolve with a light sweep reads as premium; a mechanical wipe line reads as cheap. Save the divider for the slider the user drags.
- **Sync secondary motion to the main event.** A shine that runs on its own timer feels random; the same shine timed to the moment the change happens feels like the cause.
- Respect `accessibilityReduceMotion` (show a still, meaningful frame), support Dynamic Type (no fixed-height text containers), mark decorative images `accessibilityHidden(true)`, and give interactive elements labels and values.
- Haptics: `.sensoryFeedback(.impact(weight: .light), trigger: index)` on page change, `.selection` while dragging. Nothing more.

Integrate per [references/integration.md](references/integration.md). When replacing an existing onboarding, **reuse its completion flag** so existing users never see the new one, and leave the old files in place (unreferenced) unless the user says to delete them.

## Step 5: Run it and check every screen

Read [references/verify.md](references/verify.md). Build for a simulator that meets the deployment target, launch, then:

- Screenshot every page. Use `-onbStartPage N` (built into the template, debug only) to open on a page directly when taps aren't available.
- For motion, capture a burst of frames across one loop and assemble them with `scripts/contact_sheet.py`. Check that labels, images and highlights are in sync at each frame, not just that something moves.
- Tap the CTA, drag every slider, swipe back and forth. If the Simulator panel tool fails, fall back to `xcrun simctl` and say what you couldn't test.
- Check a small phone (iPhone SE/16e), the largest Dynamic Type size, and Reduce Motion on.

Fix what you find and re-check. Then relaunch the app on page 0 so it's ready for the user.

## Step 6: Report

Tell the user, briefly: what each screen does, what was generated (count, first-try or regenerated, time), what bugs you found and fixed, **what you could not test**, and any shipping caveats (illustrative images, exposed keys, old onboarding left in place). Send a contact sheet of the screens. Offer next steps: more screens, a paywall hand-off, motion clips from the stills, or a different look.
