import SwiftUI
import AVFoundation

// A muted, looping video as a background layer (for image-to-video clips made from the stills).
// Encode clips as HEVC .mp4/.mov, 3–5 s, under ~2 MB, and add them to the app target (not the asset catalog).
// With Reduce Motion on, show the clip's first frame as a still image instead.

struct LoopingVideo: UIViewRepresentable {
    let resource: String
    var ext = "mp4"
    var gravity: AVLayerVideoGravity = .resizeAspectFill

    func makeUIView(context: Context) -> PlayerView {
        let view = PlayerView()
        view.playerLayer.videoGravity = gravity
        if let url = Bundle.main.url(forResource: resource, withExtension: ext) {
            let player = AVQueuePlayer()
            player.isMuted = true
            player.preventsDisplaySleepDuringVideoPlayback = false
            context.coordinator.looper = AVPlayerLooper(player: player, templateItem: AVPlayerItem(url: url))
            view.playerLayer.player = player
            player.play()
        }
        return view
    }

    func updateUIView(_ view: PlayerView, context: Context) {}

    func makeCoordinator() -> Coordinator { Coordinator() }

    final class Coordinator {
        var looper: AVPlayerLooper?
    }

    final class PlayerView: UIView {
        override class var layerClass: AnyClass { AVPlayerLayer.self }
        var playerLayer: AVPlayerLayer { layer as! AVPlayerLayer }
    }
}
