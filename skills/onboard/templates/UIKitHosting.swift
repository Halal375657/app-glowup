import SwiftUI
import UIKit

// Presenting the SwiftUI onboarding from a UIKit app. See references/integration.md for where to call it.

final class OnboardingHostingController: UIHostingController<OnboardingFlow> {
    init(onFinish: @escaping () -> Void) {
        super.init(rootView: OnboardingFlow {
            UserDefaults.standard.set(true, forKey: OnboardingFlow.completedKey)
            onFinish()
        })
        view.backgroundColor = .black
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) { fatalError("init(coder:) is not supported") }

    override var preferredStatusBarStyle: UIStatusBarStyle { .lightContent }
}

extension UIWindow {
    /// Swap the root view controller with a cross-dissolve (e.g. onboarding → main tab bar).
    func setRoot(_ controller: UIViewController, animated: Bool = true) {
        guard animated, rootViewController != nil else {
            rootViewController = controller
            makeKeyAndVisible()
            return
        }
        UIView.transition(with: self, duration: 0.4, options: .transitionCrossDissolve) {
            let wasEnabled = UIView.areAnimationsEnabled
            UIView.setAnimationsEnabled(false)
            self.rootViewController = controller
            UIView.setAnimationsEnabled(wasEnabled)
        }
    }
}

// Example, in SceneDelegate.scene(_:willConnectTo:options:) or wherever the root is chosen:
//
//     if UserDefaults.standard.bool(forKey: OnboardingFlow.completedKey) {
//         window.rootViewController = MainTabBarController()
//     } else {
//         window.rootViewController = OnboardingHostingController { [weak window] in
//             window?.setRoot(MainTabBarController())
//         }
//     }
//     window.makeKeyAndVisible()
//
// Or present it modally from an existing controller:
//
//     let onboarding = OnboardingHostingController { [weak self] in self?.dismiss(animated: true) }
//     onboarding.modalPresentationStyle = .fullScreen
//     present(onboarding, animated: true)
