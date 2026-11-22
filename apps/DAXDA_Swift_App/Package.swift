// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "DAXDAApp",
    platforms: [
        .macOS(.v14),
        .iOS(.v17)
    ],
    products: [
        .executable(
            name: "DAXDAApp",
            targets: ["DAXDAApp"]
        )
    ],
    dependencies: [],
    targets: [
        .executableTarget(
            name: "DAXDAApp",
            dependencies: [],
            path: "Sources/DAXDAApp"
        )
    ]
)

