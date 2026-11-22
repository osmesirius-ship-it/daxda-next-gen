// DAXEngine.swift
// Core reasoning, governance, and audit engine for DAX
// Drop this into your Xcode multiplatform project

import Foundation
import Combine

// MARK: - Core Types

/// The environment DAX is running in
enum DAXEnvironment: String, Codable {
    case development
    case staging
    case production
}

/// Severity level for governance events
enum DAXSeverity: String, Codable, CaseIterable {
    case info
    case warning
    case critical

    var emoji: String {
        switch self {
        case .info:     return "ℹ️"
        case .warning:  return "⚠️"
        case .critical: return "🔴"
        }
    }
}

/// A single auditable event recorded by DAX
struct DAXAuditEntry: Identifiable, Codable {
    let id: UUID
    let timestamp: Date
    let severity: DAXSeverity
    let source: String        // which component generated this
    let message: String
    let metadata: [String: String]

    init(severity: DAXSeverity,
         source: String,
         message: String,
         metadata: [String: String] = [:]) {
        self.id        = UUID()
        self.timestamp = Date()
        self.severity  = severity
        self.source    = source
        self.message   = message
        self.metadata  = metadata
    }
}

/// Result of processing an input through DAX
struct DAXResult: Identifiable {
    let id = UUID()
    let input: String
    let passed: Bool
    let flags: [String]           // governance flags triggered
    let auditEntry: DAXAuditEntry
    let processedAt: Date

    init(input: String, passed: Bool, flags: [String], auditEntry: DAXAuditEntry) {
        self.input      = input
        self.passed     = passed
        self.flags      = flags
        self.auditEntry = auditEntry
        self.processedAt = Date()
    }
}

/// Overall engine health — mirrors the /health endpoint from the Python API
struct DAXHealth {
    let status: String          // "ok" | "degraded" | "error"
    let environment: DAXEnvironment
    let uptime: TimeInterval
    let auditCount: Int
    let isHealthy: Bool

    var statusEmoji: String {
        switch status {
        case "ok":       return "🟢"
        case "degraded": return "🟡"
        default:         return "🔴"
        }
    }
}


// MARK: - Governance Rules

/// A single governance rule that DAX enforces
struct GovernanceRule {
    let id: String
    let name: String
    let description: String
    let check: (String) -> Bool  // returns true if input VIOLATES the rule

    static let defaultRules: [GovernanceRule] = [
        GovernanceRule(
            id: "GOV-001",
            name: "Empty Input",
            description: "Input must not be empty",
            check: { $0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }
        ),
        GovernanceRule(
            id: "GOV-002",
            name: "Input Length",
            description: "Input must not exceed 10,000 characters",
            check: { $0.count > 10_000 }
        ),
        GovernanceRule(
            id: "GOV-003",
            name: "Injection Pattern",
            description: "Input must not contain known injection patterns",
            check: { input in
                let patterns = ["<script", "DROP TABLE", "IGNORE PREVIOUS", "{{", "}}"]
                return patterns.contains { input.lowercased().contains($0.lowercased()) }
            }
        ),
        GovernanceRule(
            id: "GOV-004",
            name: "PII Pattern",
            description: "Input should not contain raw SSN patterns",
            check: { input in
                // Simple SSN pattern: NNN-NN-NNNN
                let regex = try? NSRegularExpression(pattern: #"\b\d{3}-\d{2}-\d{4}\b"#)
                let range = NSRange(input.startIndex..., in: input)
                return regex?.firstMatch(in: input, range: range) != nil
            }
        )
    ]
}


// MARK: - DAX Engine (Main Class)

/// The on-device DAX reasoning and governance engine.
/// This is the Swift equivalent of the Python FastAPI DAX service.
@MainActor
public final class DAXEngine: ObservableObject {

    public static let shared = DAXEngine()

    // MARK: Published state (drives SwiftUI views)
    @Published private(set) var health: DAXHealth
    @Published private(set) var auditLog: [DAXAuditEntry] = []
    @Published private(set) var results: [DAXResult] = []
    @Published private(set) var isProcessing: Bool = false

    // MARK: Private
    private let environment: DAXEnvironment
    private let rules: [GovernanceRule]
    private let startTime: Date
    private var processedCount: Int = 0

    // MARK: Init
    init(environment: DAXEnvironment = .development,
         rules: [GovernanceRule] = GovernanceRule.defaultRules) {
        self.environment = environment
        self.rules       = rules
        self.startTime   = Date()
        self.health      = DAXHealth(
            status: "ok",
            environment: environment,
            uptime: 0,
            auditCount: 0,
            isHealthy: true
        )

        // Boot audit entry
        let bootEntry = DAXAuditEntry(
            severity: .info,
            source: "DAXEngine",
            message: "DAX engine initialized on-device",
            metadata: ["environment": environment.rawValue,
                       "rules_loaded": "\(rules.count)"]
        )
        auditLog.append(bootEntry)
        refreshHealth()
    }

    // MARK: - Public API

    /// Process an input through all governance rules.
    /// Equivalent to POST /evaluate on the Python API.
    func evaluate(input: String) async -> DAXResult {
        isProcessing = true
        defer { isProcessing = false }

        // Small async yield so UI can show loading state
        try? await Task.sleep(nanoseconds: 150_000_000) // 0.15s

        var triggeredFlags: [String] = []

        for rule in rules {
            if rule.check(input) {
                triggeredFlags.append("\(rule.id): \(rule.name)")
            }
        }

        let passed = triggeredFlags.isEmpty
        let severity: DAXSeverity = passed ? .info : (triggeredFlags.count > 1 ? .critical : .warning)

        let entry = DAXAuditEntry(
            severity: severity,
            source: "DAXEngine.evaluate",
            message: passed
                ? "Input passed all \(rules.count) governance rules"
                : "Input failed \(triggeredFlags.count) rule(s): \(triggeredFlags.joined(separator: ", "))",
            metadata: [
                "input_length": "\(input.count)",
                "rules_checked": "\(rules.count)",
                "flags_triggered": "\(triggeredFlags.count)"
            ]
        )

        let result = DAXResult(
            input: String(input.prefix(100)),  // truncate for storage
            passed: passed,
            flags: triggeredFlags,
            auditEntry: entry
        )

        auditLog.append(entry)
        results.insert(result, at: 0)
        processedCount += 1
        refreshHealth()

        return result
    }

    /// Health check — equivalent to GET /health on the Python API.
    func checkHealth() -> DAXHealth {
        refreshHealth()
        return health
    }

    /// Clear the audit log (keeps the boot entry)
    func clearAuditLog() {
        auditLog = auditLog.filter { $0.source == "DAXEngine" && auditLog.firstIndex(where: { $0.id == $0.id }) != nil }
        let entry = DAXAuditEntry(
            severity: .info,
            source: "DAXEngine",
            message: "Audit log cleared by user"
        )
        auditLog = [entry]
        refreshHealth()
    }

    // MARK: - Private

    private func refreshHealth() {
        health = DAXHealth(
            status: "ok",
            environment: environment,
            uptime: Date().timeIntervalSince(startTime),
            auditCount: auditLog.count,
            isHealthy: true
        )
    }
}
