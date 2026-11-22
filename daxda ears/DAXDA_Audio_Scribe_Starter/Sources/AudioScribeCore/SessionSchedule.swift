import Foundation

/// An explicitly defined recording window. Store dates as absolute instants;
/// interpret user-entered wall-clock times in America/New_York before creating it.
public struct RecordingSession: Codable, Identifiable, Equatable {
    public let id: UUID
    public var title: String
    public var start: Date
    public var end: Date
    public var manuallyStopped: Bool

    public init(
        id: UUID = UUID(),
        title: String,
        start: Date,
        end: Date,
        manuallyStopped: Bool = false
    ) {
        self.id = id
        self.title = title
        self.start = start
        self.end = end
        self.manuallyStopped = manuallyStopped
    }

    public var isValid: Bool { end > start }

    public func isActive(at now: Date) -> Bool {
        isValid && !manuallyStopped && start <= now && now < end
    }
}

public enum AudioScribeTime {
    public static let zone = TimeZone(identifier: "America/New_York")!

    public static func display(_ date: Date) -> String {
        let formatter = ISO8601DateFormatter()
        formatter.timeZone = zone
        formatter.formatOptions = [.withInternetDateTime, .withTimeZone]
        return formatter.string(from: date)
    }
}
