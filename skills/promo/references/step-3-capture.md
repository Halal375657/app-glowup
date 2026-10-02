# Step 3: Capture the real app

## Set up the Simulator

```bash
xcrun simctl list devices available | grep -E "^-- iOS|iPhone"
ID=<udid of a current iPhone Pro, e.g. iPhone 17 Pro>   # 1206×2622 native; scales cleanly to 886×1920 and 1320×2868
xcrun simctl boot $ID 2>/dev/null; open -a Simulator
xcrun simctl ui $ID appearance dark          # or light, to match the plan
xcrun simctl privacy $ID grant photos <bundle-id>    # pre-grant so no alert appears mid-shot
xcrun simctl addmedia $ID work/demo/*.jpg            # demo photos into the library
python3 <skill-dir>/scripts/sim_record.py clean $ID  # 9:41, full battery and signal
```

Build and install the app (see the `/onboard` verify reference or the project's own scheme), then put it in the state the shot needs: skip onboarding (set its completion flag with `xcrun simctl spawn $ID defaults write <bundle-id> <key> -bool YES`), sign in to a test account, unlock premium with a debug flag. Never record real account data.

## Record a shot

Open the app on the right screen **before** you start recording. Recording from launch captures the home screen with the user's personal apps on it.

```bash
python3 <skill-dir>/scripts/sim_record.py start $ID <output-dir>/work/capture/S1-raw.mov
# drive the shot: Simulator tool taps/swipes, or deep links (xcrun simctl openurl $ID myapp://...)
python3 <skill-dir>/scripts/sim_record.py stop <output-dir>/work/capture/S1-raw.mov
```

Driving the shot:

- Prefer the iOS Simulator tool (`tap`, `swipe`, `touch_path`) so the interaction is real. Move deliberately: wait ~0.6 s after each screen settles before the next action, so the viewer can read it.
- A slow, eased `touch_path` drag looks far better than a fast swipe for sliders and before/after reveals.
- The Simulator never shows a finger. That's correct for App Store previews; for ads, add a tap indicator in compose if the action isn't obvious.
- If the feature waits on a server, record the whole wait, then cut it in compose (or speed it up and label nothing as "instant" unless it is).
- Record each beat as its own file. Retakes are cheap; editing around a fumble is not.

## Trim to constant frame rate

simctl records variable frame rate (frames only when the screen changes). Convert every clip:

```bash
python3 <skill-dir>/scripts/sim_record.py trim work/capture/S1-raw.mov work/capture/S1.mp4 1.2 6.4 --fps 30
```

## Review

```bash
mkdir -p work/review && ffmpeg -v error -i work/capture/S1.mp4 -vf "fps=2,scale=300:-1,tile=8x2" -frames:v 1 work/review/S1.png
```

Look at every sheet: correct screen, no home screen or other apps, no personal data, no debug overlays or Xcode banners, no unexpected alerts or keyboard, status bar clean, the result actually visible and held long enough. Confirm every interaction you performed actually shows up (a drag that didn't register looks identical to no drag). Re-record failures.

When done: `python3 <skill-dir>/scripts/sim_record.py reset $ID`.

## Stills for screenshots

Capture the exact frames for the App Store screenshots now, from the app itself (not from video):

```bash
xcrun simctl io $ID screenshot "$(pwd)/work/capture/shot-01.png"   # absolute path: simctl resolves relative paths elsewhere
```
