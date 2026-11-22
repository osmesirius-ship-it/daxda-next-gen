# Installation and permission steps

## Prerequisites
- A Mac running macOS 14.2 or later is recommended for the planned system-audio capture path.
- Xcode and Command Line Tools installed.
- The app must be built and signed locally. This starter is not signed/notarized.

## Developer setup
1. Unzip the project.
2. Open Terminal and `cd` into the `DAXDA_Audio_Scribe_Starter` folder.
3. Review `CONFIGURATION.md` and `TEST_PLAN.md`.
4. Create/open a macOS App target in Xcode and add the `Sources` files to the target. Add the permission strings from `Sources/AudioScribeMacApp/Info.plist.template` to the target's Info settings.
5. Implement and wire the native microphone and ScreenCaptureKit adapters before enabling recording. The starter deliberately does not claim to capture audio yet.
6. Set the app's signing team and bundle identifier in Xcode. Run the app locally.
7. When the app requests microphone access, approve it only if expected. In System Settings → Privacy & Security → Microphone, enable the app if it appears.
8. For system audio, use System Settings → Privacy & Security → Screen & System Audio Recording (wording may vary by macOS release). Enable the app if listed. Grant audio-only access where available; do not grant screen capture unless the chosen API requires it.
9. Configure a local storage directory inside the user's Library/Application Support folder. Do not request Full Disk Access.
10. Add a user-level background/login item only after the session scheduler, visible status, and stop override pass the acceptance tests. The login item must not start recording by itself.
11. Create a test session and validate with a harmless test tone and spoken test phrase. Verify separate files, timestamps, visible indicator, stop behavior, and no network egress.
12. Do not use for sensitive conversations until consent, retention, access controls, and local transcription behavior have been reviewed.

## Permission strings
Use the strings in `Sources/AudioScribeMacApp/Info.plist.template`. macOS permission prompts are tied to the signed app identity. If permissions are denied, the app must remain in a non-recording state and explain the required setting.
