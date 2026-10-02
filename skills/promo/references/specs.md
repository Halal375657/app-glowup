# Platform specs and rules

Checked 2026-10-02 against official pages. Platforms change these; when something fails upload, re-check the source. `scripts/check_specs.py` enforces the "hard" rows.

## App Store app preview (iPhone)

Source: App Store Connect Help, "App preview specifications"; App Review Guidelines 2.3.4; developer.apple.com/app-store/app-previews.

| Item | Spec |
|---|---|
| Size | **886×1920** portrait (or 1920×886 landscape). Accepted for 6.9", 6.5", 6.3", 6.1". 5.5" uses 1080×1920. |
| Duration | **15–30 s** |
| Frame rate | **30 fps max** |
| Video | H.264, progressive, High Profile up to Level 4.0, 10–12 Mbps; or ProRes 422 HQ (.mov) |
| Audio | Stereo AAC **256 kbps**, 44.1 or 48 kHz. Include a track even if silent (silent previews: unconfirmed, so don't risk it). |
| File | .mp4/.mov/.m4v, ≤ 500 MB |
| Count | Up to 3 per localization |
| Poster | Defaults to the frame at **5 s**; make 5 s the strongest settled frame. |

Content: **screen captures of the app only** (2.3.4). Text/video overlays and narration allowed. No people, hands, device frames, or rendered/AI footage. No prices or seasonal references (2.3.7). Disclose required IAP/subscription/login. 4+ appropriate (2.3.8). You must own all rights, including music, and show fictional account data (2.3.9).

## App Store screenshots (iPhone)

Source: App Store Connect Help, "Screenshot specifications"; Guideline 2.3.3.

| Item | Spec |
|---|---|
| Size | **1320×2868** (6.9"; also 1290×2796, 1260×2736). One 6.9" set scales down to 6.5"/6.3"/6.1". |
| Format | PNG or JPEG, **no alpha** |
| Count | 1–10 per localization |

Content: must show the app in use (2.3.3). Captions, backgrounds and device frames are fine. No prices.

## Meta (Instagram/Facebook)

Source: Meta Ads Guide (Reels, Facebook Feed).

| Placement | Size | Notes |
|---|---|---|
| Reels / Stories | 9:16, 1080×1920 (1440×2560 recommended max) | H.264, fixed frame rate, stereo AAC ≥128 kbps, ≤4 GB |
| Feed | 4:5, 1080×1350 (1440×1800) | 1:1 also runs in feed |

**Reels safe zone:** keep text, logos and faces out of the top **14%**, bottom **35%** and **6%** at each side. At 1080×1920: top 270 px, bottom 672 px, sides 65 px. (Stories: roughly top 14%, bottom 20%.)

Text: primary text works best under 125 characters (Reels shows ~44 before "more"); headline ~27–40.

## TikTok in-feed

Source: TikTok Ads Help, "Auction In-Feed Ads".

9:16 (≥540×960; deliver 1080×1920), also 1:1 and 16:9. ≤ 500 MB, ≥ 516 kbps. Ad text: no links, @ or hashtags; keep under 100 characters. Display name 20 characters. Use the reel safe zone above (TikTok's caption and buttons cover similar areas). **AI-generated content must be labeled** with the AIGC toggle. Music in ads must come from the Commercial Music Library or be licensed.

## Google (App campaigns, YouTube Shorts)

App campaigns: up to 5 headlines × **30** characters, 5 descriptions × **90** characters; videos 16:9, 9:16 or 1:1, 10–60 s, uploaded to YouTube. Shorts: 9:16, under 60 s recommended.

## AI people and testimonials

FTC rule 16 CFR 465 (in force Oct 2024) bans fake or false testimonials, including from people who don't exist; AI-generated fake reviews are covered. An AI presenter demonstrating the app is not banned; an AI "customer" describing results is. Keep every claim truthful. TikTok requires the AIGC label; Meta auto-labels detected AI. Never use a real person's likeness without consent.

## Music

Ads need music cleared for commercial use: TikTok Commercial Music Library, Meta Sound Collection, your own license, or generated music whose provider terms allow commercial use. Popular tracks from in-app libraries are not cleared for ads. The App Store requires you to own the rights (2.3.9).
