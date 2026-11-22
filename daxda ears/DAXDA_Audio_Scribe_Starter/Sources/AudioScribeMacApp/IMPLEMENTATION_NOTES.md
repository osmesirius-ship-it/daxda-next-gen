# Native adapter implementation notes

This file is a checklist for the next coding phase, not a claim that capture has been implemented.

## Microphone adapter
- Use AVAudioEngine input and check microphone authorization before starting.
- Write audio to a session-scoped local file using AVAudioFile.
- Stop the engine and close the file on manual stop, scheduled end, permission loss, or error.
- Avoid blocking the main thread in audio callbacks.

## System-audio adapter
- Use ScreenCaptureKit's audio capture APIs for the selected process/system audio supported by the chosen macOS release.
- Check system-audio authorization before starting.
- Keep the output audio-only; do not request or persist video frames.
- Write audio buffers to a separate file and log dropped buffers/stream errors.
- Verify actual audio content in tests; successful stream creation is not enough.

## Scheduler and UI
- Build a SwiftUI menu-bar application with a persistent `Recording` state, source indicators, current session, elapsed time, and a prominent Stop button.
- Let the user create/edit/delete explicit session windows. Persist them locally.
- A user-level launch agent may start the scheduler, but it must not enable capture unless an explicitly defined session is active and permissions pass.
- Manual Stop sets `manuallyStopped = true` for that session and persists the override.
- Do not restart a manually stopped session until the user explicitly re-arms it.

## DAXDA connector
- Use a local process/interface or local files as the boundary.
- Original audio and source transcript remain immutable.
- Analysis outputs must reference session ID, transcript segment ID, and time range.
- Do not make claims of verification based only on transcription or model-generated interpretation.
