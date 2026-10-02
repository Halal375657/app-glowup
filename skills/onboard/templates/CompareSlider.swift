import SwiftUI

// Drag-to-compare page. On first show it plays a hint: starts on Before, wipes to After,
// settles in the middle. Light haptics while dragging; VoiceOver can adjust it.

struct ComparePage: View {
    let isActive: Bool
    var before = "onb-before"
    var after = "onb-after"
    var eyebrow = "Drag to compare"
    var headline = "Same input.\nBetter result."
    /// Keep this label while the images are generated rather than real app output.
    var footnote: String? = "Illustrative example"

    @State private var split: CGFloat = 0.5
    @State private var appeared = false
    @State private var hasHinted = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        VStack(alignment: .leading, spacing: 22) {
            VStack(alignment: .leading, spacing: 10) {
                Text(eyebrow)
                    .font(OnbTheme.eyebrow).tracking(2.5)
                    .textCase(.uppercase)
                    .foregroundStyle(OnbTheme.accent)
                Text(headline)
                    .font(OnbTheme.headline)
                    .foregroundStyle(.white)
            }
            .reveal(appeared, delay: 0.1)

            CompareSlider(before: before, after: after, split: $split)
                .aspectRatio(2 / 3, contentMode: .fit)
                .frame(maxWidth: .infinity)
                .reveal(appeared, delay: 0.25)

            if let footnote {
                Text(footnote)
                    .font(.footnote)
                    .foregroundStyle(.white.opacity(0.45))
                    .frame(maxWidth: .infinity)
            }
        }
        .padding(.horizontal, 24)
        .padding(.top, 8)
        .padding(.bottom, 130)
        .frame(maxHeight: .infinity, alignment: .top)
        .background {
            RadialGradient(colors: [OnbTheme.accent.opacity(0.18), .clear], center: .top, startRadius: 0, endRadius: 500)
                .ignoresSafeArea()
        }
        .onChange(of: isActive, initial: true) { _, active in
            guard active else { return }
            appeared = true
            guard !hasHinted, !reduceMotion else { return }
            hasHinted = true
            split = 0.98
            Task { @MainActor in
                try? await Task.sleep(for: .seconds(0.9))
                withAnimation(.easeInOut(duration: 1.4)) { split = 0.02 }
                try? await Task.sleep(for: .seconds(1.8))
                withAnimation(.spring(duration: 0.9, bounce: 0.25)) { split = 0.5 }
            }
        }
    }
}

struct CompareSlider: View {
    let before: String
    let after: String
    @Binding var split: CGFloat
    var beforeLabel = "Before"
    var afterLabel = "After"

    var body: some View {
        GeometryReader { geo in
            let w = geo.size.width, h = geo.size.height
            ZStack {
                photo(after)
                photo(before)
                    .mask(alignment: .leading) { Rectangle().frame(width: w * split) }

                // Divider + glowing handle
                Rectangle().fill(.white).frame(width: 2, height: h)
                    .shadow(color: OnbTheme.accent, radius: 8)
                    .position(x: w * split, y: h / 2)
                Circle()
                    .fill(.ultraThinMaterial)
                    .overlay(Circle().stroke(.white, lineWidth: 2))
                    .overlay(Image(systemName: "chevron.left.chevron.right").font(.footnote.bold()))
                    .frame(width: 44, height: 44)
                    .shadow(color: OnbTheme.accent.opacity(0.8), radius: 12)
                    .position(x: w * split, y: h * 0.55)

                HStack {
                    label(beforeLabel).opacity(split > 0.18 ? 1 : 0)
                    Spacer()
                    label(afterLabel).opacity(split < 0.82 ? 1 : 0)
                }
                .padding(14)
                .frame(maxHeight: .infinity, alignment: .top)
                .animation(.easeOut(duration: 0.2), value: split > 0.18)
                .animation(.easeOut(duration: 0.2), value: split < 0.82)
            }
            .clipShape(.rect(cornerRadius: 28))
            .overlay(RoundedRectangle(cornerRadius: 28).stroke(.white.opacity(0.12), lineWidth: 1))
            .contentShape(.rect)
            .gesture(DragGesture(minimumDistance: 0).onChanged { split = min(max($0.location.x / w, 0.02), 0.98) })
            .sensoryFeedback(.selection, trigger: split < 0.5)
            .accessibilityElement()
            .accessibilityLabel("\(beforeLabel) and \(afterLabel) comparison")
            .accessibilityValue("Showing \(Int((1 - split) * 100)) percent \(afterLabel)")
            .accessibilityAdjustableAction { dir in
                split = min(max(split + (dir == .increment ? -0.1 : 0.1), 0.02), 0.98)
            }
        }
    }

    private func photo(_ name: String) -> some View {
        Image(name).resizable().scaledToFill()
    }

    private func label(_ text: String) -> some View {
        Text(text)
            .font(.caption.weight(.semibold))
            .padding(.horizontal, 12).padding(.vertical, 7)
            .background(.ultraThinMaterial, in: .capsule)
    }
}
