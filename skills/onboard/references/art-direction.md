# Art direction and generation on fal

## Models

Check what exists before using a name; fal's catalog changes.

```bash
python3 scripts/fal_gen.py models gpt-image      # search the catalog
python3 scripts/fal_gen.py check                 # verify FAL_KEY and show prices (free)
```

Defaults (GPT Image 2.5 on fal):

| Endpoint | Use |
|---|---|
| `openai/gpt-image-2.5/flare/text-to-image` | Default. Fast, natural lighting, supports transparent backgrounds. |
| `openai/gpt-image-2.5/flare/edit` | Change one thing in an existing image and keep everything else. Use for every pair. |
| `openai/gpt-image-2.5/sunburst/text-to-image` | Slower, higher detail. Try only if flare fails on fine detail. |

Sizes: `1024x1536` (portrait, full-screen heroes and cards), `1024x1024` (icons, objects), `1536x1024` (wide banners). Each image takes about 25 seconds.

## The style lock

Write one paragraph and append it to every prompt in the set:

> Soft 3D clay render, rounded shapes, matte materials. Lighting: large soft key light from above-left, warm rim light in the brand coral (#FF6B4A). Background: smooth cream-to-peach gradient. Gentle ambient occlusion, shallow depth of field. No text, no logos, no watermark.

Include the brand accent hex in the lighting or palette. Say where text will sit ("the bottom third fades into near-black empty space for text overlay") so the art leaves room for the headline.

## Prompt recipe

1. Medium and genre ("Glossy luxury skincare advertisement photograph", "Soft 3D clay render", "Flat pastel vector illustration").
2. Subject, framing and expression, specifically (age range, pose, crop, where the subject sits in the frame).
3. The detail that proves the feature (a cluttered desk; a full inbox; a faded old photo).
4. Realism guard for people: "natural skin texture and pores, not plastic".
5. The style lock.
6. Exclusions: no text, logos, watermark, hands (hands go wrong most often), jewelry if irrelevant.

## Edit pairs (before/after, variants)

Generate the image that is hardest to get right first, then derive the others with `flare/edit`, passing the first as `--ref` (a URL printed by the script, or a local path):

> Edit this exact photo. [The one change, described concretely.] Keep everything else identical: same person, same identity, same expression, same pose, same framing and crop, same lighting, same background, same hair, same colors. Natural skin texture. No other changes.

Both directions work: generate the clean "after" and edit to *add* the problem, or generate the "before" and edit to *remove* it. Then check alignment:

```bash
python3 scripts/pair_check.py before.png after.png --box 300,250,724,520 --out pair.png
```

`outside` should be under about 4 and `inside` clearly higher. If `outside` is high, the edit moved the face; regenerate with stronger "keep identical" wording.

For apps that change one attribute while keeping the subject (lighting, background, colour, season, style), make each variant an edit of the same base image.

## Transparent assets

Use `--bg transparent` with flare and ask for "isolated object on a transparent background, no shadow on the ground". Save as PNG (`add_to_assets.py --png`). Check the edges on both a dark and a light background.

## Using the app's real output

If the app's own pipeline can produce the after (or the user has real results with consent), use that instead of a generated after. It's more honest and often more convincing. Real screenshots of the app's UI can be passed as `--ref` to generate art in a matching palette.

## Checking images

Open every image and look for: extra or merged fingers, warped text, doubled features, plastic skin, the feature not actually visible at phone size, a subject crop that collides with the headline area. Regenerate only what fails, fixing the prompt, and say so in the report.

## Size budget

Photos as JPEG quality 85, long edge 1536 at most: about 300–450 KB each. Video loops as HEVC, 3–5 s, under 2 MB each. Tell the user the total added to the app.
