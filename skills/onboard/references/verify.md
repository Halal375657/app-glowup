# Building and checking in the Simulator

## Build and launch

```bash
# Pick an available iPhone on a runtime >= the deployment target
xcrun simctl list devices available | grep -E "^-- iOS|iPhone"
ID=<udid>
xcrun simctl boot $ID 2>/dev/null; open -a Simulator

# -workspace App.xcworkspace when CocoaPods is used
xcodebuild -project App.xcodeproj -scheme App -destination "id=$ID" \
  -derivedDataPath build CODE_SIGNING_ALLOWED=NO build 2>&1 | grep -E "error:|BUILD (SUCCEEDED|FAILED)"

APP=$(ls -d build/Build/Products/Debug-iphonesimulator/*.app | head -1)
BID=$(/usr/libexec/PlistBuddy -c "Print CFBundleIdentifier" "$APP/Info.plist")
xcrun simctl install $ID "$APP"
xcrun simctl launch $ID $BID
```

If the app already finished onboarding on this simulator, reset the flag before launching:

```bash
xcrun simctl spawn $ID defaults write $BID hasCompletedOnboarding -bool NO   # use the app's real key
```

Prefer the iOS Simulator tool (`attach` before building, `launch`, `screenshot`, `tap`, `swipe`) when it is available; it lets you test interaction. If it fails, use `simctl` as above and say in the report which interactions you could not test.

## Open on a specific page

The template reads `onbStartPage` in debug builds:

```bash
xcrun simctl terminate $ID $BID; xcrun simctl launch $ID $BID -onbStartPage 1
```

## Screenshots and motion

```bash
S=<scratch dir>
xcrun simctl io $ID screenshot $S/p0.png
# A burst across one animation loop (about 1 frame/second)
for i in $(seq 1 8); do xcrun simctl io $ID screenshot $S/f$i.png >/dev/null 2>&1; sleep 0.9; done
python3 scripts/contact_sheet.py $S/f*.png --out $S/loop.png --scale 0.3
# Zoom into the area that changes to check sync
python3 scripts/contact_sheet.py $S/f*.png --out $S/zoom.png --crop 0,180,1000,560 --scale 0.4 --cols 4
```

Look at the sheet and ask: is each label right for the image it sits on? Does the highlight cross during the change? Does anything jump, clip, or sit under the status bar or Dynamic Island? A blank first screenshot usually means the app was still launching; wait and retake before debugging.

## Checklist

- [ ] Every page screenshotted on a current iPhone (Pro size)
- [ ] Status bar: full-bleed art runs behind the clock and Dynamic Island with no black strip above it, and no label or pill sits under them
- [ ] Small phone (iPhone SE / 16e): headline and CTA don't collide, nothing clipped
- [ ] Largest Dynamic Type: `xcrun simctl ui $ID content_size extra-extra-extra-large`, then reset with `large`
- [ ] Reduce Motion on: the hero shows a meaningful still (Settings → Accessibility → Motion, or check the code path)
- [ ] Light mode, if the app supports it: `xcrun simctl ui $ID appearance light`
- [ ] CTA advances and finishes; the flag is saved; relaunch goes straight to the app
- [ ] Sliders drag, swipes page both ways, haptic triggers compile
- [ ] Permission primers trigger the real prompt only on tap, and the app has the usage description
- [ ] No key in any file: `grep -rnE "FAL_KEY *=|Authorization: Key [A-Za-z0-9]" . --exclude-dir=build`
