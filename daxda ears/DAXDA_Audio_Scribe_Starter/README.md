# DAXDA Audio Scribe — macOS starter

Status: **starter scaffold / not yet installed or production-validated**.

## Locked requirements
- Inputs: microphone + system audio.
- Storage: local device only.
- Session policy: explicitly defined sessions only (no always-on recording).
- Time zone: `America/New_York`.
- Retention: until manually deleted.
- Visible recording state and an immediate manual stop override.
- Permission-gated; no network upload or cloud transcription in this starter.

## Important limitation
This package is a build scaffold and implementation contract, not a signed, notarized, production-ready app. The system-audio capture adapter must be completed and tested against the target macOS version using Apple's ScreenCaptureKit APIs. Do not treat a successful build of the scheduler/UI as proof that system audio is being captured.

## Proposed deliverables
1. `Sources/AudioScribeCore/SessionSchedule.swift` — explicit session model and schedule checks.
2. `Sources/AudioScribeCore/RecordingState.swift` — fail-closed state model and stop override.
3. `Sources/AudioScribeMacApp/Info.plist.template` — required permission strings.
4. `CONFIGURATION.md` — fixed decisions and implementation contract.
5. `INSTALL.md` — local development and permission setup.
6. `TEST_PLAN.md` — acceptance gates before real recordings.

## Target
macOS 14.2+ recommended for the planned ScreenCaptureKit process-audio route. Use Xcode on the Mac to build, sign, and grant permissions. The scaffold intentionally does not claim capture is operational until the native adapters and end-to-end tests are complete.
