import Foundation

public enum CaptureSource: String, Codable, CaseIterable {
    case microphone
    case systemAudio = "system_audio"
}

public enum RecordingState: Equatable {
    case idle
    case waitingForSession
    case checkingPermissions
    case recording(sessionID: UUID)
    case stoppedByUser(sessionID: UUID)
    case blocked(reason: String)
    case failed(reason: String)
}

/// Policy model for the app coordinator. Actual capture adapters must enforce this
/// policy rather than relying on UI state alone.
public struct CapturePolicy: Codable, Equatable {
    public var localOnly: Bool = true
    public var visibleIndicatorRequired: Bool = true
    public var manualStopOverridesSchedule: Bool = true
    public var uploadEnabled: Bool = false
    public var retentionUntilManuallyDeleted: Bool = true

    public init() {}
}
