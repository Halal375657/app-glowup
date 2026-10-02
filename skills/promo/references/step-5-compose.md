# Step 5: Compose with Hyperframes

## The brief

Write `<output-dir>/composition-brief.md` first. It is the boundary: `/promo` decides *what* (angle, shots, copy, claims, safe zones, specs); Hyperframes decides *how* (structure, animation mechanics, lint rules).

```markdown
# Composition brief: [App] — [feature]
## Outputs
- reel 1080x1920 15 s × hooks [a, b, c]; feed 1080x1350; square 1080x1080; preview 886x1920 [20] s; screenshots 1320x2868 × [n]; overlays (transparent)
## Source
- Footage: assets/S1.mp4 (what it shows, useful in/out points), assets/S2.mp4 ...
- Stills: assets/shot-01.png ...
- Brand: background [hex], accent [hex], fonts [files]
- Copy that must appear verbatim: [lines from the grounded claims list]
## Creative
- Tone, angle, hook ideas (from promo-plan.md), storyboard per format (copy the tables)
- Avoid: generic ad language, claims not in the grounded list, text in safe zones
## Hyperframes
Load hyperframes-core, hyperframes-animation, hyperframes-creative, hyperframes-keyframes, hyperframes-cli, media-use.
/promo is its own workflow: don't enter the `hyperframes` intent interview or its product-launch-video workflow.
```

## Project layout

One small Hyperframes project per output shape, sharing assets through symlinks (`check` and `render` work on a project folder's `index.html`):

```
composition/
  shared/assets/   footage, stills, generated art, music      shared/kit/   copy of <skill-dir>/kit/
  launch/  reel/  feed/  square/  preview/  overlay/  hooks/  screens/  each: index.html, assets -> ../shared/assets, kit -> ../shared/kit, hyperframes.json, meta.json
```

Start from the templates in `<skill-dir>/kit/templates/` (tested on a real run). They are starting points: rewrite scenes, copy and timing for the plan, keep the structural rules below.

| Template | Output |
|---|---|
| `launch.html` | Launch video, 1920×1080, 15–25 s (see `launch.md`) |
| `reel.html` | 9:16 ad; hook variants via the `hook` variable (`--variables '{"hook":"b"}'`) |
| `box.template.html` + `make_box.py` | 4:5 feed and 1:1 square from one layout (phone left, words right) |
| `preview.html` | App Store preview: captures only, caption band, strongest frame at 5 s |
| `overlay.html` | Phone with the feature on a transparent background (UGC kit) |
| `hooks.html` | Hook caption alone on transparent (UGC kit) |
| `screens.html` | App Store screenshots via the `n` variable |
| `kit/promo.css` | Phone frame, captions, pills, CTA, end card, safe-area helper, bundled fonts |

## Rules that came from real bugs

- **A timed `<video>` can't sit inside a timed element.** Put footage at the root (or in an untimed wrapper) with its own `data-start`/`data-duration`/`data-media-start`; scenes are separate timed `<section class="clip">`s. Mind paint order: root-level footage after a section covers it, so give captions a higher `z-index`.
- **Animate the untimed wrapper** (the `.phone`), never the timed `<video>`.
- **Captions never cover the feature.** If the ad is about a detail in the photo, the caption isn't on that detail. Check every hook frame.
- **Keep the feature out of the platform UI.** For reels: text, faces and the product inside top 270 px / bottom 672 px / sides 65 px. Shift footage (`top:` on its wrapper) rather than letting the key detail sit under the top bar.
- **Crop proof shots tight.** A full-screen still at card size makes the difference invisible; zoom on the area that changes (fixed-pixel offsets, so taller cards don't reveal UI text below).
- **Hide the app's own copy when it fights the ad's text** (a scrim), or use it as the copy.
- **Short display titles break deliberately** into separate block elements (never `<br>`, never an accidental widow like "Keep your / face."), with line-height ≥ 1.1 for serif display type (`check` flags overlapping lines).
- **Transparent outputs** need `background: transparent` on `html`, `body` and `#root`, and render with `--format mov` (ProRes 4444) and `--format webm` (VP9 alpha).
- **App Store preview:** captures only, no `.phone` frame, no generated art. Scaling the capture down on a brand background with a caption band is fine.
- Fonts must be bundled files (`kit/fonts`), or `lint` fails; GSAP from the CDN is the Hyperframes default.

## Check and review (the gate)

```bash
cd composition/reel && npx hyperframes check            # 0 errors; read the warnings
npx hyperframes render --quality draft --variables '{"hook":"a"}' -o ../../work/renders/reel-a-draft.mp4
python3 <skill-dir>/scripts/review_frames.py ../../work/renders/reel-a-draft.mp4 --out ../../work/review/reel-a.png \
  --at 0.3,1,1.6,2.4,3.5,5,7,9.5,13,14.5 --zone reel
```

Look at the sheet for every hook and format: is the key detail visible in the hook, outside the red zones, uncovered by captions? Is every line readable and settled long enough? Does any transition show a muddy double exposure? Fix and re-render drafts until it's right; `check` passing is necessary, not sufficient.
