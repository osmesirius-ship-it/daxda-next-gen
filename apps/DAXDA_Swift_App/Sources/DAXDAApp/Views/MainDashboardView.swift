//
//  MainDashboardView.swift
//  DAXDA.IA — Autonomous Invariant Intelligence
//

import SwiftUI

public struct MainDashboardView: View {
    @StateObject private var engine = DAXEngine.shared
    @State private var inputPrompt: String = ""
    @State private var lastResult: DAXResult?
    @State private var selectedTab: Int = 0

    public init() {}

    public var body: some View {
        TabView(selection: $selectedTab) {
            // Tab 1: Celestial Avatar
            CelestialAvatarView()
                .tabItem {
                    Label("Avatar", systemImage: "sparkles")
                }
                .tag(0)

            // Tab 2: Invariant Governance Console
            NavigationStack {
                ZStack {
                    Color(red: 0.04, green: 0.03, blue: 0.08).ignoresSafeArea()

                    ScrollView {
                        VStack(spacing: 20) {
                            // Header banner
                            HStack {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text("Nicole Protocol (886-Ops)")
                                        .font(.caption)
                                        .foregroundStyle(Color.pink)
                                        .monospaced()
                                    Text("Invariant Evaluation Engine")
                                        .font(.title2.bold())
                                        .foregroundStyle(Color.white)
                                }
                                Spacer()
                                Circle()
                                    .fill(engine.health.isHealthy ? Color.green : Color.red)
                                    .frame(width: 12, height: 12)
                            }
                            .padding()
                            .background(Color.white.opacity(0.05))
                            .clipShape(RoundedRectangle(cornerRadius: 16))

                            // Input Box
                            VStack(alignment: .leading, spacing: 10) {
                                Text("Input Claim or Reasoning Prompt:")
                                    .font(.subheadline)
                                    .foregroundStyle(Color.gray)

                                TextField("Enter claim to test against AOG-1...", text: $inputPrompt)
                                    .textFieldStyle(.plain)
                                    .padding(14)
                                    .background(Color.white.opacity(0.08))
                                    .clipShape(RoundedRectangle(cornerRadius: 12))
                                    .foregroundStyle(Color.white)

                                Button {
                                    Task {
                                        guard !inputPrompt.isEmpty else { return }
                                        let text = inputPrompt
                                        inputPrompt = ""
                                        let res = await engine.evaluate(input: text)
                                        lastResult = res
                                    }
                                } label: {
                                    HStack {
                                        if engine.isProcessing {
                                            ProgressView()
                                                .tint(.black)
                                        } else {
                                            Image(systemName: "shield.checkerboard")
                                            Text("Evaluate with Nicole Protocol")
                                                .bold()
                                        }
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(
                                        LinearGradient(
                                            colors: [Color.pink, Color.purple],
                                            startPoint: .leading,
                                            endPoint: .trailing
                                        )
                                    )
                                    .foregroundStyle(.white)
                                    .clipShape(RoundedRectangle(cornerRadius: 12))
                                }
                                .disabled(engine.isProcessing)
                            }
                            .padding()
                            .background(Color.white.opacity(0.04))
                            .clipShape(RoundedRectangle(cornerRadius: 16))

                            // Latest Result
                            if let res = lastResult {
                                VStack(alignment: .leading, spacing: 8) {
                                    HStack {
                                        Text(res.passed ? "✅ INVARIANT PASS" : "⛔ AOG-1 TRIPPED / FAIL")
                                            .font(.headline)
                                            .foregroundStyle(res.passed ? Color.green : Color.red)
                                        Spacer()
                                        Text("Score: \(res.auditEntry.severity.emoji)")
                                    }

                                    Text(res.auditEntry.message)
                                        .font(.subheadline)
                                        .foregroundStyle(Color.white.opacity(0.9))

                                    if !res.flags.isEmpty {
                                        Text("Triggered Flags: \(res.flags.joined(separator: ", "))")
                                            .font(.caption)
                                            .foregroundStyle(Color.yellow)
                                    }
                                }
                                .padding()
                                .background(res.passed ? Color.green.opacity(0.12) : Color.red.opacity(0.12))
                                .clipShape(RoundedRectangle(cornerRadius: 14))
                            }

                            // Audit History
                            VStack(alignment: .leading, spacing: 12) {
                                Text("On-Device Audit Log (\(engine.auditLog.count))")
                                    .font(.headline)
                                    .foregroundStyle(Color.white)

                                ForEach(engine.auditLog.prefix(5)) { entry in
                                    HStack(alignment: .top) {
                                        Text(entry.severity.emoji)
                                        VStack(alignment: .leading, spacing: 2) {
                                            Text(entry.message)
                                                .font(.caption)
                                                .foregroundStyle(Color.white.opacity(0.85))
                                            Text(entry.source)
                                                .font(.caption2)
                                                .foregroundStyle(Color.gray)
                                        }
                                        Spacer()
                                    }
                                    .padding(8)
                                    .background(Color.white.opacity(0.03))
                                    .clipShape(RoundedRectangle(cornerRadius: 8))
                                }
                            }
                            .padding()
                            .background(Color.white.opacity(0.04))
                            .clipShape(RoundedRectangle(cornerRadius: 16))
                        }
                        .padding()
                    }
                }
                .navigationTitle("Governance")
            }
            .tabItem {
                Label("Engine", systemImage: "cpu")
            }
            .tag(1)

            // Tab 3: DePIN Telemetry
            NavigationStack {
                ZStack {
                    Color(red: 0.04, green: 0.03, blue: 0.08).ignoresSafeArea()
                    VStack(spacing: 24) {
                        Text("🌐 DAXDA Global DePIN Mesh")
                            .font(.title2.bold())
                            .foregroundStyle(Color.white)

                        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 16) {
                            MetricCard(title: "Active Nodes", value: "1,001", subtitle: "Edge RTX 3090 / H100", color: .cyan)
                            MetricCard(title: "Sealed Blocks", value: "18,031+", subtitle: "SHA-256 Merkle Chain", color: .pink)
                            MetricCard(title: "Verified Txs", value: "1.80M+", subtitle: "Proof-of-Execution", color: .purple)
                            MetricCard(title: "Slashes / Escapes", value: "0 / 0", subtitle: "100% Invariant Security", color: .green)
                        }

                        VStack(alignment: .leading, spacing: 8) {
                            Text("Consensus Mechanism")
                                .font(.headline)
                                .foregroundStyle(Color.white)
                            Text("Epidemic P2P Mesh with bit-parallel Cayley table sign masks in Cl(16,4). Continuous local loopback telemetry to Sovereign Physical Worker.")
                                .font(.subheadline)
                                .foregroundStyle(Color.gray)
                        }
                        .padding()
                        .background(Color.white.opacity(0.04))
                        .clipShape(RoundedRectangle(cornerRadius: 16))

                        Spacer()
                    }
                    .padding()
                }
                .navigationTitle("DePIN Mesh")
            }
            .tabItem {
                Label("DePIN", systemImage: "network")
            }
            .tag(2)
        }
        .tint(Color.pink)
    }
}

struct MetricCard: View {
    let title: String
    let value: String
    let subtitle: String
    let color: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.caption)
                .foregroundStyle(Color.gray)
            Text(value)
                .font(.title.bold())
                .foregroundStyle(color)
            Text(subtitle)
                .font(.caption2)
                .foregroundStyle(Color.white.opacity(0.7))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color.white.opacity(0.05))
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }
}

