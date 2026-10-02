# Step 1: Inspect the app and the features

## The app

```bash
find . -maxdepth 3 \( -name "*.xcodeproj" -o -name "*.xcworkspace" \) -not -path "*/Pods/*"
plutil -p */Info.plist 2>/dev/null | grep -E "CFBundleDisplayName|CFBundleURLSchemes|UsageDescription" | head
find . -name "*.colorset" -not -path "*/Pods/*" | head -20
ls fastlane/metadata 2>/dev/null; find . -iname "*app*store*" -o -iname "*marketing*" -o -iname "*metadata*" | grep -v Pods | head
```

Collect: display name, bundle ID, brand colors (hex from colorsets), fonts, app icon (`AppIcon.appiconset`, largest PNG), URL schemes (for deep links), and the App Store copy if the user has it (subtitle, description, promotional text, What's New). Ask the user for the store listing text or URL if it isn't in the repo; it is the best source of grounded claims.

## Each feature

For every feature in scope:

1. **Find it in code.** Search view controllers/views, string files and analytics event names for the feature's words. Read the screen(s) that run it.
2. **The before → after.** What does the user have before (a shoebox of paper receipts), and what do they get (a categorized monthly budget)? This is the ad.
3. **The 2–3 beats of using it.** Entry → key action → result (pick photo → tap "Open eyes" → result slider). These are the shots to record.
4. **The demo path in the Simulator.** How to get there quickly and repeatably:
   - Deep link (`xcrun simctl openurl <udid> myapp://...`) if a URL scheme routes there.
   - Launch arguments or a debug flag that opens the screen (ask before adding one; keep it `#if DEBUG`).
   - Otherwise the tap path from launch, written down step by step for the Simulator tool.
   - Note anything that blocks a clean run: login, paywall, onboarding, permission alerts, network calls, rate limits. Plan around them (a test account, a debug entitlement flag, pre-granted permissions with `xcrun simctl privacy <udid> grant photos <bundle-id>`).
5. **Demo content.** What goes into the feature: photos, text, data. Use content you have the rights to: generated images (step 4), the user's own approved samples, or licensed stock. Never a real person's photo without consent. Add photos to the Simulator with `xcrun simctl addmedia <udid> <files>`.
6. **Real output.** Does the feature call a server or AI model? Then the result in the recording is real output, which is what makes the ad honest. Check it works in the Simulator (network, API keys in the debug build).

## Grounded claims list

Write down, with the source of each: the app's name and tagline, the feature's name as the app shows it, every number or capability you might put on screen ("in one tap", "in seconds", "50+ categories"), any real ratings or reviews (exact quotes, with the user's permission to use them). Anything not on this list can't appear as a claim.

## Rubric (answer per feature before planning)

1. What does it do, in one sentence a stranger understands?
2. Who is it for, and what moment in their life makes them want it?
3. What is the before → after?
4. What are the 2–3 beats of using it?
5. What is the visual hook (the single frame that makes someone stop scrolling)?
6. Which grounded claims support it?
7. How do you reach it in the Simulator, and what could block a clean recording?
8. What demo content will you use, and do you have the rights?
9. What is the one-line pitch for the ad copy?

Also confirm: the app builds and runs on a booted Simulator that meets its deployment target.
