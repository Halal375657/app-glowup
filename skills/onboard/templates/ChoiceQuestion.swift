import SwiftUI

// A personalization question with animated cards. The answer is saved under
// `storageKey` (UserDefaults) so the app can read it later (default goal, first template, and so on).

struct ChoiceQuestionPage: View {
    let isActive: Bool
    var question = "What do you want to do first?"
    var options: [(symbol: String, title: String)] = [
        ("chart.pie", "Budgets"), ("doc.text.viewfinder", "Receipts"), ("bell", "Reminders"), ("target", "Goals"),
    ]
    var storageKey = "onbChoice"

    @State private var selection: String?
    @State private var appeared = false

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            Text(question)
                .font(OnbTheme.headline)
                .foregroundStyle(.white)
                .reveal(appeared, delay: 0.1)

            LazyVGrid(columns: [GridItem(.flexible(), spacing: 14), GridItem(.flexible(), spacing: 14)], spacing: 14) {
                ForEach(Array(options.enumerated()), id: \.offset) { i, option in
                    let selected = selection == option.title
                    Button {
                        withAnimation(.spring(duration: 0.4, bounce: 0.3)) { selection = option.title }
                        UserDefaults.standard.set(option.title, forKey: storageKey)
                    } label: {
                        VStack(alignment: .leading, spacing: 14) {
                            Image(systemName: option.symbol)
                                .font(.title2)
                                .foregroundStyle(selected ? .black : OnbTheme.accent)
                                .symbolEffect(.bounce, value: selected)
                            Text(option.title)
                                .font(.headline)
                                .foregroundStyle(selected ? .black : .white)
                        }
                        .frame(maxWidth: .infinity, minHeight: 110, alignment: .topLeading)
                        .padding(16)
                        .background(selected ? OnbTheme.accent : .white.opacity(0.07), in: .rect(cornerRadius: 22))
                        .overlay(RoundedRectangle(cornerRadius: 22).stroke(.white.opacity(selected ? 0 : 0.12)))
                        .scaleEffect(selected ? 1.03 : 1)
                    }
                    .buttonStyle(.plain)
                    .accessibilityAddTraits(selected ? .isSelected : [])
                    .reveal(appeared, delay: 0.2 + Double(i) * 0.07)
                }
            }
            .sensoryFeedback(.selection, trigger: selection)

            Spacer(minLength: 0)
        }
        .padding(.horizontal, 24)
        .padding(.top, 24)
        .padding(.bottom, 140)
        .onChange(of: isActive, initial: true) { _, active in
            if active { appeared = true }
            if selection == nil { selection = UserDefaults.standard.string(forKey: storageKey) }
        }
    }
}
