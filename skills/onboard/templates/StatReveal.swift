import SwiftUI

// A ring that fills while a number counts up to it. For fitness, finance, habit and
// productivity apps: "the result you'll get", made tangible.

struct StatRevealPage: View {
    let isActive: Bool
    var value: Double = 87          // final number shown
    var fraction: Double = 0.87     // how full the ring ends up (0...1)
    var unit = "%"
    var caption = "of users hit their goal in 4 weeks"
    var eyebrow = "APP NAME"
    var headline = "Results you\ncan see."

    @State private var progress = 0.0
    @State private var appeared = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        VStack(spacing: 36) {
            VStack(alignment: .leading, spacing: 10) {
                Text(eyebrow).font(OnbTheme.eyebrow).tracking(2.5).foregroundStyle(OnbTheme.accent)
                Text(headline).font(OnbTheme.headline).foregroundStyle(.white)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .reveal(appeared, delay: 0.1)

            ZStack {
                Circle().stroke(.white.opacity(0.08), lineWidth: 22)
                Circle()
                    .trim(from: 0, to: progress * fraction)
                    .stroke(AngularGradient(colors: [OnbTheme.accent.opacity(0.4), OnbTheme.accent], center: .center),
                            style: StrokeStyle(lineWidth: 22, lineCap: .round))
                    .rotationEffect(.degrees(-90))
                    .shadow(color: OnbTheme.accent.opacity(0.6), radius: 16)
                VStack(spacing: 4) {
                    Text("\(Int((progress * value).rounded()))\(unit)")
                        .font(.system(size: 64, weight: .bold, design: .rounded))
                        .monospacedDigit()
                        .contentTransition(.numericText(value: progress * value))
                        .foregroundStyle(.white)
                    Text(caption)
                        .font(.subheadline)
                        .multilineTextAlignment(.center)
                        .foregroundStyle(.white.opacity(0.6))
                        .frame(maxWidth: 180)
                }
            }
            .frame(width: 260, height: 260)
            .reveal(appeared, delay: 0.25)
            .accessibilityElement(children: .ignore)
            .accessibilityLabel("\(Int(value))\(unit) \(caption)")

            Spacer(minLength: 0)
        }
        .padding(.horizontal, 28)
        .padding(.top, 24)
        .padding(.bottom, 140)
        .onChange(of: isActive, initial: true) { _, active in
            guard active, !appeared else { return }
            appeared = true
            if reduceMotion {
                progress = 1
            } else {
                withAnimation(.easeOut(duration: 1.6).delay(0.5)) { progress = 1 }
            }
        }
        .sensoryFeedback(.success, trigger: progress == 1)
    }
}
