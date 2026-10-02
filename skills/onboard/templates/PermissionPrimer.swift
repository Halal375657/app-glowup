import SwiftUI
import AVFoundation
import Photos
import UserNotifications

// Explains why the app needs a permission, then shows the real system prompt only when the
// user taps. Requires the matching NS...UsageDescription in Info.plist, or the app crashes.

enum OnbPermission {
    case camera, photos, notifications

    var symbol: String {
        switch self {
        case .camera: "camera.fill"
        case .photos: "photo.on.rectangle.angled"
        case .notifications: "bell.badge.fill"
        }
    }

    @MainActor
    func request() async -> Bool {
        switch self {
        case .camera:
            return await AVCaptureDevice.requestAccess(for: .video)
        case .photos:
            let status = await PHPhotoLibrary.requestAuthorization(for: .readWrite)
            return status == .authorized || status == .limited
        case .notifications:
            return (try? await UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .badge, .sound])) ?? false
        }
    }
}

struct PermissionPrimerPage: View {
    let isActive: Bool
    var permission: OnbPermission = .photos
    var headline = "Pick a photo.\nWe do the rest."
    var reasons = ["Only the photos you choose are used", "Edits happen on your device", "Nothing is posted anywhere"]
    var buttonTitle = "Allow photo access"
    /// Called after the system prompt closes, with the result. Advance the flow here.
    var onDone: (Bool) -> Void = { _ in }

    @State private var appeared = false
    @State private var pulse = false

    var body: some View {
        VStack(alignment: .leading, spacing: 28) {
            ZStack {
                Circle().fill(OnbTheme.accent.opacity(0.12)).frame(width: 120, height: 120)
                    .scaleEffect(pulse ? 1.12 : 1)
                    .animation(.easeInOut(duration: 1.6).repeatForever(autoreverses: true), value: pulse)
                Image(systemName: permission.symbol)
                    .font(.system(size: 44, weight: .semibold))
                    .foregroundStyle(OnbTheme.accent)
                    .symbolEffect(.bounce, value: appeared)
            }
            .frame(maxWidth: .infinity)
            .reveal(appeared, delay: 0.1)
            .accessibilityHidden(true)

            Text(headline).font(OnbTheme.headline).foregroundStyle(.white)
                .reveal(appeared, delay: 0.2)

            VStack(alignment: .leading, spacing: 14) {
                ForEach(Array(reasons.enumerated()), id: \.offset) { i, reason in
                    Label {
                        Text(reason).foregroundStyle(.white.opacity(0.8))
                    } icon: {
                        Image(systemName: "checkmark.circle.fill").foregroundStyle(OnbTheme.accent)
                    }
                    .reveal(appeared, delay: 0.3 + Double(i) * 0.08)
                }
            }

            Spacer(minLength: 0)

            Button {
                Task { onDone(await permission.request()) }
            } label: {
                Text(buttonTitle)
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 17)
                    .foregroundStyle(.black)
                    .background(OnbTheme.accent, in: .capsule)
            }
        }
        .padding(.horizontal, 24)
        .padding(.top, 40)
        .padding(.bottom, 24)
        .onChange(of: isActive, initial: true) { _, active in
            if active { appeared = true; pulse = true }
        }
    }
}
