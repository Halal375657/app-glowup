import SwiftUI

// Container for the onboarding: paged screens, page dots, CTA button, entrance animation,
// and the completion flag. Copy into the app, rename the brand values, and replace the pages.

/// Brand values used by every onboarding view. Set these from the app's own colors and fonts.
enum OnbTheme {
    static let accent = Color(red: 124 / 255, green: 156 / 255, blue: 255 / 255)   // brand accent (#7C9CFF)
    static let background = Color.black
    static let headline = Font.system(size: 38, weight: .bold, design: .serif)
    static let eyebrow = Font.caption.weight(.semibold)
}

struct OnboardingFlow: View {
    /// Use the app's existing key when replacing an old onboarding, so existing users skip this one.
    static let completedKey = "hasCompletedOnboarding"

    var onFinish: () -> Void

    #if DEBUG
    // Launch with `-onbStartPage 1` to open on a specific page.
    @State private var index = UserDefaults.standard.integer(forKey: "onbStartPage")
    #else
    @State private var index = 0
    #endif

    /// One CTA label per page. Its count is the page count.
    private let ctas = ["See it work", "Get started"]

    var body: some View {
        ZStack(alignment: .bottom) {
            OnbTheme.background.ignoresSafeArea()

            TabView(selection: $index) {
                // Each page gets `isActive` so it can start its animation when shown.
                // Replace these with the planned screens.
                ExamplePage(isActive: index == 0, title: "Your hook,\nin one line.").tag(0)
                ExamplePage(isActive: index == 1, title: "Then show\nhow it works.").tag(1)
            }
            .tabViewStyle(.page(indexDisplayMode: .never))
            // Required: without it the pager stops at the status bar, and full-bleed pages show a
            // black strip above the photo even though they ignore the safe area themselves.
            .ignoresSafeArea()

            VStack(spacing: 20) {
                PageDots(count: ctas.count, index: index)
                Button {
                    if index == ctas.count - 1 { onFinish() } else { withAnimation(.smooth) { index += 1 } }
                } label: {
                    Text(ctas[min(index, ctas.count - 1)])
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 17)
                        .foregroundStyle(.black)
                        .background(OnbTheme.accent, in: .capsule)
                        .shadow(color: OnbTheme.accent.opacity(0.45), radius: 18, y: 6)
                        .contentTransition(.opacity)
                        .animation(.smooth, value: index)
                }
                .sensoryFeedback(.impact(weight: .light), trigger: index)
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 12)
        }
        .preferredColorScheme(.dark)
    }
}

/// Placeholder page showing the standard layout: eyebrow, headline, subline, staggered entrance.
private struct ExamplePage: View {
    let isActive: Bool
    let title: String
    @State private var appeared = false

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Spacer()
            Text("APP NAME")
                .font(OnbTheme.eyebrow).tracking(2.5)
                .foregroundStyle(OnbTheme.accent)
                .reveal(appeared, delay: 0.1)
            Text(title)
                .font(OnbTheme.headline)
                .foregroundStyle(.white)
                .reveal(appeared, delay: 0.25)
            Text("One specific sentence about what the user gets.")
                .foregroundStyle(.white.opacity(0.7))
                .reveal(appeared, delay: 0.4)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 28)
        .padding(.bottom, 150)
        // Pages in a paged TabView don't get onAppear reliably; drive animations from isActive.
        .onChange(of: isActive, initial: true) { _, active in
            if active { appeared = true }
        }
    }
}

// MARK: - Shared pieces

struct PageDots: View {
    let count: Int
    let index: Int

    var body: some View {
        HStack(spacing: 8) {
            ForEach(0..<count, id: \.self) { i in
                Capsule()
                    .fill(i == index ? OnbTheme.accent : .white.opacity(0.3))
                    .frame(width: i == index ? 24 : 8, height: 8)
            }
        }
        .animation(.smooth, value: index)
        .accessibilityHidden(true)
    }
}

extension View {
    /// Fade, rise and un-blur into place once `shown` becomes true.
    func reveal(_ shown: Bool, delay: Double) -> some View {
        modifier(Reveal(shown: shown, delay: delay))
    }
}

private struct Reveal: ViewModifier {
    let shown: Bool
    let delay: Double
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    func body(content: Content) -> some View {
        content
            .opacity(shown ? 1 : 0)
            .offset(y: shown || reduceMotion ? 0 : 20)
            .blur(radius: shown || reduceMotion ? 0 : 6)
            .animation(.smooth(duration: 0.7).delay(delay), value: shown)
    }
}

/// Top safe-area inset of the key window, for full-bleed pages that ignore the safe area
/// but still need to keep labels clear of the status bar and Dynamic Island.
@MainActor
var onbWindowTopInset: CGFloat {
    (UIApplication.shared.connectedScenes.first as? UIWindowScene)?.windows.first?.safeAreaInsets.top ?? 47
}

#Preview {
    OnboardingFlow {}
}
