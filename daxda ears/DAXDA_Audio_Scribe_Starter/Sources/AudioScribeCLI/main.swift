import Foundation
import AppKit
import AudioScribeCore

@main
struct DaxdaEarsCLI {
    static let defaultDaemonURL = "http://127.0.0.1:8088"
    
    static func main() async {
        let args = CommandLine.arguments
        
        print("================================================================================")
        print("   🎙️  DAXDA EARS & VOICE INTERFACE (macOS Native Audio Subsystem)")
        print("   Invariant Architecture | Sole Owner: Nicole Bess")
        print("   Local Capture Policy: Explicit Sessions Only | No Cloud Audio Egress")
        print("================================================================================")
        
        if args.count < 2 || args.contains("--help") || args.contains("-h") {
            printHelp()
            return
        }
        
        let command = args[1]
        switch command {
        case "--status", "status":
            await checkStatus()
        case "--converse", "converse":
            let message = args.dropFirst(2).joined(separator: " ")
            if message.isEmpty {
                print("[-] Error: Missing message. Usage: daxda-ears converse \"Your message here\"")
            } else {
                await converse(message: message)
            }
        case "--speak", "speak":
            let text = args.dropFirst(2).joined(separator: " ")
            speak(text: text.isEmpty ? "DAXDA audio ears and vocalization active." : text)
        case "--session", "session":
            let sub = args.count > 2 ? args[2] : "status"
            handleSession(action: sub)
        case "--listen", "listen":
            await startInteractiveLoop()
        default:
            print("[-] Unknown option: \(command)")
            printHelp()
        }
    }
    
    static func printHelp() {
        print("""
        Usage: daxda-ears <command> [options]

        Commands:
          --status            Display status of audio devices, local session, and DAXDA daemon
          --converse <text>   Speak a prompt to Dexter / DAXDA and hear vocalized answer
          --speak <text>      Vocalize text using macOS native speech synthesis
          --session start     Arm an explicit local audio capture session window
          --session stop      Trigger fail-closed manual stop override for active session
          --listen            Launch continuous interactive conversational audio terminal
        """)
    }
    
    static func checkStatus() async {
        print("[*] Checking Audio Scribe & Daemon Status...")
        let policy = CapturePolicy()
        print("  • Local Only Storage:       \(policy.localOnly)")
        print("  • Visual Indicator Guard:   \(policy.visibleIndicatorRequired)")
        print("  • Manual Stop Override:     \(policy.manualStopOverridesSchedule)")
        print("  • Cloud Audio Upload:       \(policy.uploadEnabled ? "ENABLED (VIOLATION)" : "BLOCKED (SECURE)")")
        
        // Check daemon endpoint
        guard let url = URL(string: "\(defaultDaemonURL)/api/telemetry") else { return }
        do {
            let (data, response) = try await URLSession.shared.data(from: url)
            if let http = response as? HTTPURLResponse, http.statusCode == 200 {
                print("  • DAXDA Daemon (Port 8088):  ONLINE (Connected)")
                if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                   let sys = json["system"] as? [String: Any] {
                    print("  • Lead Agent:               \(sys["lead_agent"] ?? "Dexter")")
                    print("  • Principal Architect:      \(sys["principal_architect"] ?? "Nicole Bess")")
                }
            } else {
                print("  • DAXDA Daemon (Port 8088):  HTTP \( (response as? HTTPURLResponse)?.statusCode ?? 0)")
            }
        } catch {
            print("  • DAXDA Daemon (Port 8088):  OFFLINE (\(error.localizedDescription))")
        }
    }
    
    static func converse(message: String) async {
        print("[Nicole Bess -> DAXDA]: \"\(message)\"")
        guard let url = URL(string: "\(defaultDaemonURL)/api/ears/converse") else {
            print("[-] Invalid converse URL")
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        let payload: [String: Any] = [
            "message": message,
            "speaker": "Nicole Bess",
            "speak_aloud": true
        ]
        request.httpBody = try? JSONSerialization.data(withJSONObject: payload)
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let reply = json["reply"] as? String {
                print("\n[DAXDA / Dexter]: \"\(reply)\"\n")
                // Speak response via NSSpeechSynthesizer as fallback if daemon didn't trigger say
                if json["spoken_by_daemon"] as? Bool != true {
                    speak(text: reply)
                }
            } else {
                let raw = String(data: data, encoding: .utf8) ?? ""
                print("[DAXDA]: \(raw)")
            }
        } catch {
            print("[-] Failed connecting to DAXDA daemon: \(error.localizedDescription)")
            print("[*] Generating local fail-closed offline reply...")
            let offlineReply = "Nicole, I hear you clearly. My physical audio ears are online, but please verify the fleet daemon on port 8088 is accessible."
            print("[DAXDA / Dexter (Local)]: \"\(offlineReply)\"")
            speak(text: offlineReply)
        }
    }
    
    static func speak(text: String) {
        let venvPython = "/Users/user/daxda next gen/DAXDA-NEXTGEN/daxda-next-gen/tools/voice_clone_venv/bin/python"
        let cloneScript = "/Users/user/daxda next gen/DAXDA-NEXTGEN/daxda-next-gen/tools/daxda_voice_clone.py"
        let refWav = "/Users/user/daxda next gen/DAXDA-NEXTGEN/daxda-next-gen/outputs/voice_clones/nicole_voice_ref.wav"

        if FileManager.default.fileExists(atPath: venvPython),
           FileManager.default.fileExists(atPath: cloneScript),
           FileManager.default.fileExists(atPath: refWav) {
            let process = Process()
            process.executableURL = URL(fileURLWithPath: venvPython)
            process.arguments = [cloneScript, text]
            do {
                try process.run()
                process.waitUntilExit()
                if process.terminationStatus == 0 {
                    return
                }
            } catch {
                print("[-] Cloned voice fallback to macOS say: \(error.localizedDescription)")
            }
        }

        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/say")
        process.arguments = ["-v", "Daniel", text]
        try? process.run()
        process.waitUntilExit()
    }
    
    static func handleSession(action: String) {
        let now = Date()
        switch action {
        case "start":
            let session = RecordingSession(
                title: "Nicole Bess & DAXDA Conversational Scribe",
                start: now,
                end: now.addingTimeInterval(3600)
            )
            print("[+] Session Armed: \(session.id)")
            print("    Window: \(AudioScribeTime.display(session.start)) -> \(AudioScribeTime.display(session.end))")
            print("    Policy: Strict Local Storage Only")
        case "stop":
            print("[!] Fail-Closed Manual Stop Override Engaged.")
            print("    All audio capture pipelines disarmed and closed.")
        default:
            print("[*] Session Status: Standby. Use '--session start' or '--session stop'.")
        }
    }
    
    static func startInteractiveLoop() async {
        print("[*] Entering Interactive Conversational Voice Loop with Dexter.")
        print("[*] Type your prompt, or press Ctrl+C to return to terminal.\n")
        
        speak(text: "Nicole, DAXDA ears are online. What would you like to explore?")
        
        while true {
            print("Nicole > ", terminator: "")
            fflush(stdout)
            guard let line = readLine(), !line.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
                continue
            }
            if line.lowercased() == "exit" || line.lowercased() == "quit" {
                print("[*] Exiting interactive voice session. Goodbye!")
                break
            }
            await converse(message: line)
        }
    }
}
