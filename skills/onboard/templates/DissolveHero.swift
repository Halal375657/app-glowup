import SwiftUI

// Screen 1 for "transform" apps: a full-bleed photo that dissolves between states on a loop,
// with a sheen of light sweeping across exactly while it changes, a slow "breathing" zoom,
// and a pill naming the current state. Works for 2+ states (before/after, or style variants).
//
// Images must be aligned edits of one base image (see references/art-direction.md),
// otherwise the dissolve shows the subject shifting.

struct DissolveHeroPage: View {
    let isActive: Bool
    /// Asset names and pill labels, in loop order. The last state gets the accent treatment.
    var states: [(image: String, label: String)] = [("onb-hero-before", "Before"), ("onb-hero", "After")]
    var eyebrow = "APP NAME"
    var headline = "Your hook,\nin one line."
    var subline = "One specific sentence about the result."

    @State private var appeared = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        GeometryReader { geo in
            ZStack(alignment: .bottom) {
                DissolveLoop(states: states,
                             size: CGSize(width: geo.size.width, height: geo.size.height * 0.78),
                             topInset: onbWindowTopInset, animated: !reduceMotion)
                    .phaseAnimator([1.0, 1.06]) { view, scale in
                        view.scaleEffect(reduceMotion ? 1 : scale, anchor: .top)
                    } animation: { _ in .easeInOut(duration: 7) }
                    .mask(LinearGradient(stops: [.init(color: .black, location: 0.6), .init(color: .clear, location: 1)],
                                         startPoint: .top, endPoint: .bottom))
                    .frame(maxHeight: .infinity, alignment: .top)
                    .accessibilityHidden(true)

                VStack(alignment: .leading, spacing: 14) {
                    Text(eyebrow)
                        .font(OnbTheme.eyebrow).tracking(2.5)
                        .foregroundStyle(OnbTheme.accent)
                        .reveal(appeared, delay: 0.1)
                    Text(headline)
                        .font(OnbTheme.headline)
                        .foregroundStyle(.white)
                        .reveal(appeared, delay: 0.25)
                    Text(subline)
                        .foregroundStyle(.white.opacity(0.7))
                        .reveal(appeared, delay: 0.4)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal, 28)
                .padding(.bottom, 150)
            }
        }
        .ignoresSafeArea(edges: .top)
        .onChange(of: isActive, initial: true) { _, active in
            if active { appeared = true }
        }
    }
}

private struct DissolveLoop: View {
    let states: [(image: String, label: String)]
    let size: CGSize
    let topInset: CGFloat
    let animated: Bool

    struct Values {
        var position: Double = 0   // fractional index into `states`
        var sheen: Double = -0.7   // sheen band position, as a fraction of width
    }

    // Per state: hold 1.7 s, change over 1.3 s. The last state holds 2.8 s, then returns in 1.2 s.
    private let hold = 1.7, change = 1.3, lastHold = 2.8, back = 1.2
    private var cycle: Double { Double(states.count - 1) * (hold + change) + lastHold + back }

    var body: some View {
        if animated && states.count > 1 {
            // One linear clock; every visual value is derived from it, so they can never drift apart.
            KeyframeAnimator(initialValue: Clock(), repeating: true) { clock in
                layers(sample(clock.t))
            } keyframes: { _ in
                KeyframeTrack(\.t) {
                    MoveKeyframe(0)
                    LinearKeyframe(cycle, duration: cycle)
                }
            }
        } else {
            layers(Values(position: Double(states.count - 1), sheen: -1))
        }
    }

    struct Clock { var t: Double = 0 }

    private func sample(_ t: Double) -> Values {
        func ease(_ x: Double) -> Double { let p = min(max(x, 0), 1); return p * p * (3 - 2 * p) }
        let segment = hold + change
        let forward = Double(states.count - 1) * segment
        if t < forward {
            let i = (t / segment).rounded(.down), local = t - i * segment
            // The sheen starts just before the change and crosses while it happens.
            let sweep = (local - (hold - 0.3)) / (change + 0.3)
            return Values(position: i + ease((local - hold) / change),
                          sheen: sweep <= 0 ? -0.7 : -0.7 + 2.4 * ease(sweep))
        }
        let local = t - forward
        return Values(position: Double(states.count - 1) * (1 - ease((local - lastHold) / back)), sheen: 1.7)
    }

    private func layers(_ v: Values) -> some View {
        ZStack {
            // Each state fades in on top of the previous one as `position` passes its index.
            ForEach(states.indices, id: \.self) { i in
                photo(states[i].image)
                    .opacity(i == 0 ? 1 : min(max(v.position - Double(i - 1), 0), 1))
            }
        }
        // Keyframes drive these values directly; don't let the parent zoom's slow animation smear them.
        .transaction { $0.animation = nil }
        .overlay {
            // An overlay, so the oversized band never affects the photo's layout.
            LinearGradient(colors: [.clear, .white.opacity(0.28), OnbTheme.accent.opacity(0.18), .clear],
                           startPoint: .leading, endPoint: .trailing)
                .frame(width: size.width * 0.5, height: size.height * 1.4)
                .rotationEffect(.degrees(18))
                .blendMode(.screen)
                .offset(x: size.width * (v.sheen - 0.5))
                .transaction { $0.animation = nil }
        }
        .overlay(alignment: .topLeading) {
            let current = min(Int(v.position.rounded()), states.count - 1)
            StatePill(label: states[current].label, highlighted: current == states.count - 1)
                .padding(.leading, 20)
                .padding(.top, topInset + 12)
        }
        .frame(width: size.width, height: size.height)
        .clipped()
    }

    private func photo(_ name: String) -> some View {
        Image(name)
            .resizable()
            .scaledToFill()
            .frame(width: size.width, height: size.height, alignment: .top)
            .clipped()
    }
}

/// A pill naming the current state; the final state glows in the accent color.
struct StatePill: View {
    let label: String
    let highlighted: Bool

    var body: some View {
        HStack(spacing: 7) {
            Circle()
                .fill(highlighted ? OnbTheme.accent : .white.opacity(0.5))
                .frame(width: 7, height: 7)
                .shadow(color: highlighted ? OnbTheme.accent : .clear, radius: 5)
            Text(label)
                .font(.caption.weight(.semibold))
                .contentTransition(.interpolate)
            if highlighted {
                Image(systemName: "sparkles")
                    .font(.caption2.weight(.semibold))
                    .foregroundStyle(OnbTheme.accent)
                    .transition(.scale.combined(with: .opacity))
            }
        }
        .padding(.horizontal, 12).padding(.vertical, 7)
        .background(.ultraThinMaterial, in: .capsule)
        .overlay(Capsule().stroke(highlighted ? OnbTheme.accent.opacity(0.6) : .white.opacity(0.15), lineWidth: 1))
        .animation(.smooth(duration: 0.35), value: label)
    }
}
