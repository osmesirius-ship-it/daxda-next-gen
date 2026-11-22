// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "DAXDA_Audio_Scribe",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .library(
            name: "AudioScribeCore",
            targets: ["AudioScribeCore"]
        ),
        .executable(
            name: "daxda-ears",
            targets: ["AudioScribeCLI"]
        )
    ],
    targets: [
        .target(
            name: "AudioScribeCore",
            dependencies: [],
            path: "Sources/AudioScribeCore"
        ),
        .executableTarget(
            name: "AudioScribeCLI",
            dependencies: ["AudioScribeCore"],
            path: "Sources/AudioScribeCLI"
        )
    ]
)
