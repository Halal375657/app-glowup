# Wiring the onboarding into the app

Use the completion key the app already has. If there is none, use `hasCompletedOnboarding` (the template's default).

## SwiftUI app (`@main struct ...: App`)

```swift
@main
struct MyApp: App {
    @AppStorage(OnboardingFlow.completedKey) private var done = false

    var body: some Scene {
        WindowGroup {
            if done {
                RootView()
            } else {
                OnboardingFlow { withAnimation(.smooth) { done = true } }
            }
        }
    }
}
```

## UIKit app (SceneDelegate / AppDelegate / storyboard)

Use `templates/UIKitHosting.swift`. Find where the root view controller is chosen (often a splash controller, `SceneDelegate.scene(_:willConnectTo:)`, or `AppDelegate` setting `window.rootViewController`) and branch there:

```swift
if !UserDefaults.standard.bool(forKey: OnboardingFlow.completedKey) {
    window.rootViewController = OnboardingHostingController { [weak window] in
        window?.setRoot(MainTabBarController())   // whatever the app shows next today
    }
} else {
    // existing path
}
```

If a splash controller decides between intro and home, replace only the line that shows the old intro.

## Replacing an existing onboarding

1. Find the old completion key (for example `UserDefaults.standard.set(true, forKey: "isIntroShown")`) and set `OnboardingFlow.completedKey` to that same string. Existing users then skip the new flow.
2. Find every place the old flow is presented and point it at the new one. Keep the old files and storyboard scenes in place but unreferenced; tell the user they can delete them once happy.
3. If the old flow did work beyond showing pages (requested ATT, logged analytics, set defaults, showed a paywall), move that work into the new flow's finish handler or the matching page.

## Paywall hand-off

Don't build a new paywall unless asked. Call the app's existing presenter from the finish handler (for UIKit, present it on top of the new root after the transition). With RevenueCat's paywall UI, present `PaywallView()` or the app's own wrapper.

## Permission primers

The real system prompt must come from a user tap on the primer's button, never automatically. Use the request APIs the app already uses (for example `PHPhotoLibrary.requestAuthorization(for: .readWrite)`, `AVCaptureDevice.requestAccess(for: .video)`, `UNUserNotificationCenter.current().requestAuthorization`). Check the matching `NS...UsageDescription` exists in `Info.plist`; without it the app crashes.

## Localization

Use plain string literals in `Text("...")` (they're `LocalizedStringKey`, so they're picked up by String Catalogs). If the app ships `Localizable.strings` or an `.xcstrings` catalog, add the new keys there and tell the user which languages still need translations.

## Build settings

Templates use iOS 17 APIs. If the deployment target is lower, wrap the animated views in `if #available(iOS 17, *)` with a static fallback, rather than raising the target without asking.
