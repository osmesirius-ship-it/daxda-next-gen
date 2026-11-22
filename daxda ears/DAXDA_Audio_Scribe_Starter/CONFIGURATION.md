# Configuration contract

```json
{
  "product": "DAXDA Audio Scribe",
  "timezone": "America/New_York",
  "audio_sources": ["microphone", "system_audio"],
  "storage_mode": "local_only",
  "session_policy": "explicit_sessions_only",
  "retention": "until_manually_deleted",
  "visible_recording_indicator_required": true,
  "manual_stop_overrides_schedule": true,
  "upload_audio": false,
  "cloud_transcription": false,
  "missing_permission_behavior": "block_capture",
  "capture_failure_behavior": "stop_and_record_gap",
  "daxda_analysis": "after_capture; preserve source evidence separately"
}
```

## Session rules
- A session must be created explicitly by the user with a start and end timestamp.
- Interpret entered local times in `America/New_York`, including daylight-saving transitions.
- Do not record outside a defined session.
- A manual stop marks the current session as cancelled/stopped; the scheduler must not restart it automatically.
- If a permission is revoked, a source disappears, disk space is insufficient, or capture becomes unhealthy, stop or fail closed and visibly notify the user.
- No hidden/background capture. Show a persistent menu-bar status while recording and a clear Stop control.
- Keep microphone and system-audio files separate, then link them with a shared session ID and timestamps.
- Never overwrite originals during transcription or analysis.
- Retention is indefinite until the user deletes records. Provide explicit delete/export controls; do not silently purge.
