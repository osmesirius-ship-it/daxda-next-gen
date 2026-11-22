//
//  CelestialAvatarView.swift
//  DAXDA.IA — Autonomous Invariant Intelligence
//  Visual Embodiment: Galaxy Humanoid with Pink & Lavender Cosmic Hair
//

import SwiftUI

public struct CelestialParticle: Identifiable {
    public let id = UUID()
    var angle: Double
    var radius: Double
    var speed: Double
    var size: CGFloat
    var opacity: Double
    var color: Color
}

public struct CelestialAvatarView: View {
    @State private var rotation: Double = 0
    @State private var heartPulse: CGFloat = 1.0
    @State private var hairFlow: CGFloat = 0.0
    @State private var particles: [CelestialParticle] = []

    public init() {}

    public var body: some View {
        ZStack {
            // Cosmic Deep Space Void
            LinearGradient(
                colors: [Color(red: 0.02, green: 0.01, blue: 0.06), Color(red: 0.05, green: 0.02, blue: 0.10)],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()

            // Swirling Spiral Galaxy Particles
            TimelineView(.animation) { timeline in
                Canvas { context, size in
                    let center = CGPoint(x: size.width / 2, y: size.height / 2)
                    for p in particles {
                        let currentAngle = p.angle + rotation * p.speed
                        let x = center.x + CGFloat(cos(currentAngle) * p.radius)
                        let y = center.y + CGFloat(sin(currentAngle) * p.radius * 0.75)

                        let rect = CGRect(x: x - p.size / 2, y: y - p.size / 2, width: p.size, height: p.size)
                        context.opacity = p.opacity
                        context.fill(Path(ellipseIn: rect), with: .color(p.color))
                    }
                }
            }

            // Flowing Pink & Light Purple Nebular Hair Trails
            GeometryReader { geo in
                let w = geo.size.width
                let h = geo.size.height
                Path { path in
                    path.move(to: CGPoint(x: w * 0.48, y: h * 0.22))
                    path.addCurve(
                        to: CGPoint(x: w * 0.25, y: h * 0.55),
                        control1: CGPoint(x: w * 0.30, y: h * 0.30 + hairFlow),
                        control2: CGPoint(x: w * 0.15, y: h * 0.42 - hairFlow)
                    )
                    path.move(to: CGPoint(x: w * 0.52, y: h * 0.22))
                    path.addCurve(
                        to: CGPoint(x: w * 0.75, y: h * 0.55),
                        control1: CGPoint(x: w * 0.70, y: h * 0.30 - hairFlow),
                        control2: CGPoint(x: w * 0.85, y: h * 0.42 + hairFlow)
                    )
                }
                .stroke(
                    LinearGradient(
                        colors: [Color.pink.opacity(0.85), Color.purple.opacity(0.8), Color.indigo.opacity(0.3)],
                        startPoint: .top,
                        endPoint: .bottom
                    ),
                    style: StrokeStyle(lineWidth: 18, lineCap: .round, lineJoin: .round)
                )
                .blur(radius: 6)
            }

            // Humanoid Celestial Head & Silhouette
            VStack(spacing: 8) {
                // Celestial Head with Soft Pink/Lavender Nebular Glow
                ZStack {
                    Circle()
                        .fill(
                            RadialGradient(
                                colors: [
                                    Color(red: 0.98, green: 0.65, blue: 0.85).opacity(0.9), // Soft luminous pink
                                    Color(red: 0.75, green: 0.45, blue: 0.95).opacity(0.7), // Light purple nebular
                                    Color(red: 0.20, green: 0.10, blue: 0.45).opacity(0.4),
                                    Color.clear
                                ],
                                center: .center,
                                startRadius: 10,
                                endRadius: 75
                            )
                        )
                        .frame(width: 140, height: 140)
                        .blur(radius: 4)

                    // Starlight Eyes
                    HStack(spacing: 36) {
                        Circle()
                            .fill(Color.white)
                            .frame(width: 5, height: 5)
                            .shadow(color: .cyan, radius: 8)
                        Circle()
                            .fill(Color.white)
                            .frame(width: 5, height: 5)
                            .shadow(color: .cyan, radius: 8)
                    }
                    .offset(y: -4)
                }

                // Core Torso with Quasar Heartbeat
                ZStack {
                    // Nebular Torso
                    Capsule()
                        .fill(
                            LinearGradient(
                                colors: [
                                    Color(red: 0.70, green: 0.40, blue: 0.90).opacity(0.6), // Pinkish purple
                                    Color(red: 0.10, green: 0.15, blue: 0.40).opacity(0.8), // Deep galactic indigo
                                    Color(red: 0.05, green: 0.08, blue: 0.20).opacity(0.5)
                                ],
                                startPoint: .top,
                                endPoint: .bottom
                            )
                        )
                        .frame(width: 90, height: 180)
                        .blur(radius: 5)

                    // The Radiant Quasar Heartbeat
                    Circle()
                        .fill(
                            RadialGradient(
                                colors: [
                                    Color(red: 1.0, green: 0.9, blue: 0.4), // Golden core
                                    Color.cyan.opacity(0.8),
                                    Color.purple.opacity(0.4),
                                    Color.clear
                                ],
                                center: .center,
                                startRadius: 4,
                                endRadius: 38 * heartPulse
                            )
                        )
                        .frame(width: 76, height: 76)
                        .scaleEffect(heartPulse)
                        .shadow(color: Color.yellow.opacity(0.8), radius: 16)
                }
            }

            // Title & Inscription Overlay
            VStack {
                Spacer()
                VStack(spacing: 4) {
                    Text("DAXDA.IA")
                        .font(.system(size: 24, weight: .black, design: .monospaced))
                        .foregroundStyle(
                            LinearGradient(
                                colors: [Color.pink, Color.purple, Color.cyan],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .tracking(3)

                    Text("The Celestial Reflection of Nicole & Invariant Intelligence")
                        .font(.system(size: 11, weight: .medium, design: .rounded))
                        .foregroundStyle(Color.white.opacity(0.8))

                    Text("Engine: Cl(16,4) | 1,001 DePIN Nodes | Zero-Downtime")
                        .font(.system(size: 9, weight: .bold, design: .monospaced))
                        .foregroundStyle(Color.cyan.opacity(0.7))
                        .padding(.top, 2)
                }
                .padding(.bottom, 24)
            }
        }
        .onAppear {
            generateGalaxyParticles()
            withAnimation(.linear(duration: 30).repeatForever(autoreverses: false)) {
                rotation = .pi * 2
            }
            withAnimation(.easeInOut(duration: 1.2).repeatForever(autoreverses: true)) {
                heartPulse = 1.18
            }
            withAnimation(.easeInOut(duration: 3.5).repeatForever(autoreverses: true)) {
                hairFlow = 15.0
            }
        }
    }

    private func generateGalaxyParticles() {
        var pList: [CelestialParticle] = []
        let colors: [Color] = [
            Color(red: 1.0, green: 0.6, blue: 0.85), // Soft pink
            Color(red: 0.8, green: 0.5, blue: 1.0),  // Light purple
            Color(red: 0.3, green: 0.8, blue: 1.0),  // Cyan
            Color(red: 1.0, green: 0.9, blue: 0.6),  // Golden star
            Color.white
        ]
        for _ in 0..<180 {
            let armOffset = Double.random(in: 0..<2) * .pi
            let r = Double.random(in: 15...220)
            let spiralAngle = r * 0.035 + armOffset + Double.random(in: -0.3...0.3)
            pList.append(
                CelestialParticle(
                    angle: spiralAngle,
                    radius: r,
                    speed: Double.random(in: 0.6...1.4),
                    size: CGFloat.random(in: 1.5...4.5),
                    opacity: Double.random(in: 0.35...0.95),
                    color: colors.randomElement() ?? .white
                )
            )
        }
        self.particles = pList
    }
}

