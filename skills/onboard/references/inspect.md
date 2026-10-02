# Step 1: Inspecting an iOS app

Spend a few minutes here; every later step depends on it. Prefer `grep`/`find` over opening whole files.

## Find the project and its shape

```bash
find . -maxdepth 3 -name "*.xcodeproj" -o -maxdepth 3 -name "*.xcworkspace" -o -maxdepth 2 -name "Package.swift" | grep -v Pods
grep -h "IPHONEOS_DEPLOYMENT_TARGET" *.xcodeproj/project.pbxproj | sort -u
grep -c "PBXFileSystemSynchronizedRootGroup" *.xcodeproj/project.pbxproj   # >0: new files in the folder are picked up automatically
ls Podfile Package.resolved Cartfile 2>/dev/null
```

- **Workspace present (CocoaPods)?** Build with `-workspace`, not `-project`.
- **Synchronized folders (Xcode 16+, `objectVersion` 77)?** Dropping a `.swift` file into the folder is enough. Otherwise new files must be added to the `.pbxproj` (`PBXFileReference`, `PBXBuildFile`, group children, and the target's Sources phase). Do that carefully, or ask the user to drag the files into Xcode.

## Entry point and existing onboarding

```bash
grep -rln "@main" --include=*.swift .
grep -rn "UIApplicationMain\|func scene(_\|window?.rootViewController\|UIMainStoryboardFile\|UISceneStoryboardFile" --include=*.swift --include=Info.plist . | grep -v Pods | head
grep -rlni "onboard\|walkthrough\|intro\|welcome\|tutorial\|getstarted" --include=*.swift . | grep -v Pods
grep -rn "UserDefaults\|@AppStorage" --include=*.swift . | grep -i "onboard\|intro\|first\|launch\|tutorial" | grep -v Pods
```

Record: how the app decides what to show first (splash → onboarding → home?), the exact completion key, and where that decision is made. The new flow must plug into the same place.

## Brand

```bash
find . -name "*.colorset" -not -path "*/Pods/*" | head -30
grep -rhoE "#[0-9A-Fa-f]{6}\b|UIColor\(red: [^)]*\)|Color\(red: [^)]*\)|UIColor\(named: \"[^\"]+\"\)|Color\(\"[^\"]+\"\)" --include=*.swift . | grep -v Pods | sort | uniq -c | sort -rn | head -20
grep -rhoE "UIFont\(name: \"[^\"]+\"|\.custom\(\"[^\"]+\"" --include=*.swift . | sort | uniq -c | sort -rn | head
plutil -p Info.plist | grep -iE "UIAppFonts|CFBundleDisplayName|UsageDescription|UIUserInterfaceStyle"
```

Read the colorset `Contents.json` files for the actual values. The most-used non-gray color is usually the accent. Look at the app icon (`AppIcon.appiconset`) and a couple of main screens (or screenshots the user provides) to get the mood: light or dark, rounded or sharp, photographic or illustrated.

## What it does and the hook

Read, in order: the README, App Store description or marketing copy if the user has it (PDFs, `fastlane/metadata`, `.json` content lists), the main feature view controllers or views, and any localized strings. Write down the core flow in one line (for example: snap a receipt → it is read and categorized → the monthly budget updates).

The hook is the before/after of that flow, made visible in one glance.

## Permissions and paywall

```bash
plutil -p Info.plist | grep UsageDescription
grep -rlnE "RevenueCat|Purchases\.|StoreKit|Product\.products|Adapty|Superwall|Qonversion" --include=*.swift . | grep -v Pods | head
```

Every permission requested in the first session gets a primer screen. If there's a paywall, find the call that presents it so the last onboarding screen can hand off to it rather than building a new one.
