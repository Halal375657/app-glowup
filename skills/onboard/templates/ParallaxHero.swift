import SwiftUI

// Layered art (background, middle, foreground) drifting at different depths on a slow loop,
// plus parallax that follows the user's finger. Generate the layers as separate transparent
// PNGs (or split one image) with matching light and palette.

struct ParallaxHeroPage: View {
    let isActive: Bool
    /// Back to front. `depth` scales how far each layer moves (0 = fixed, 1 = most).
    var layers: [(image: String, depth: CGFloat)] = [("onb-layer-back", 0.2), ("onb-layer-mid", 0.5), ("onb-layer-front", 1)]
    var eyebrow = "APP NAME"
    var headline = "Your hook,\nin one line."

    @State private var appeared = false
    @State private var drag: CGSize = .zero
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        GeometryReader { geo in
            ZStack(alignment: .bottom) {
                ZStack {
                    ForEach(layers.indices, id: \.self) { i in
                        let layer = layers[i]
                        Image(layer.image)
                            .resizable()
                            .scaledToFill()
                            .frame(width: geo.size.width * 1.15, height: geo.size.height * 0.75)
                            .offset(x: drag.width * 0.08 * layer.depth, y: drag.height * 0.05 * layer.depth)
                            // Slow ambient drift, stronger for nearer layers.
                            .phaseAnimator([0.0, 1.0]) { view, phase in
                                view.offset(y: reduceMotion ? 0 : (phase - 0.5) * 14 * layer.depth)
                                    .scaleEffect(reduceMotion ? 1 : 1 + phase * 0.03 * layer.depth)
                            } animation: { _ in .easeInOut(duration: 6) }
                            // Layers fly in from depth on first show.
                            .scaleEffect(appeared || reduceMotion ? 1 : 1 + 0.15 * layer.depth)
                            .opacity(appeared ? 1 : 0)
                            .animation(.smooth(duration: 1.1).delay(Double(i) * 0.12), value: appeared)
                    }
                }
                .frame(width: geo.size.width, height: geo.size.height * 0.75)
                .clipped()
                .frame(maxHeight: .infinity, alignment: .top)
                .accessibilityHidden(true)

                VStack(alignment: .leading, spacing: 14) {
                    Text(eyebrow).font(OnbTheme.eyebrow).tracking(2.5)
                        .foregroundStyle(OnbTheme.accent)
                        .reveal(appeared, delay: 0.3)
                    Text(headline).font(OnbTheme.headline).foregroundStyle(.white)
                        .reveal(appeared, delay: 0.45)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal, 28)
                .padding(.bottom, 150)
            }
            .contentShape(.rect)
            // Simultaneous, so horizontal page swipes in the TabView keep working.
            .simultaneousGesture(
                DragGesture()
                    .onChanged { if !reduceMotion { drag = $0.translation } }
                    .onEnded { _ in withAnimation(.spring(duration: 0.8, bounce: 0.2)) { drag = .zero } }
            )
        }
        .ignoresSafeArea(edges: .top)
        .onChange(of: isActive, initial: true) { _, active in
            if active { appeared = true }
        }
    }
}
