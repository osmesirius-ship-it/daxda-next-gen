# Acceptance test plan

Do not label the system production-ready until every required test passes.

## Permissions and safety
- [ ] Microphone denied → capture is blocked; no recording file created.
- [ ] System-audio permission denied → system capture is blocked; UI explains why.
- [ ] Permission revoked mid-session → capture stops/fails closed and a gap event is written.
- [ ] Visible recording indicator remains present throughout capture.
- [ ] Manual Stop immediately stops both sources and prevents scheduled restart.
- [ ] App launch or login does not start recording outside an explicitly defined session.
- [ ] No audio or transcript is transmitted over the network.

## Scheduling
- [ ] Only user-created sessions trigger capture.
- [ ] Session start/end use `America/New_York`, including DST boundary tests.
- [ ] Sleep/wake and reboot during a session are handled explicitly; no silent catch-up recording.
- [ ] Overlapping sessions are rejected or merged with a clear user-visible rule.
- [ ] Stop override persists for the current session.

## Evidence and storage
- [ ] Microphone and system audio are saved separately and linked by session ID.
- [ ] Each segment records UTC timestamp plus configured local timezone.
- [ ] Manifest records source, app version, permission status, start/end, interruptions, and hashes.
- [ ] Original audio remains immutable; transcript/analysis are separate derived artifacts.
- [ ] No automatic deletion; explicit delete action removes selected session and associated derivatives.
- [ ] Disk-full and write-error conditions stop capture safely and report loss.

## Quality and integration
- [ ] Confirm both audio tracks actually contain expected signals.
- [ ] Measure timestamp drift and dropped frames over a 60-minute test.
- [ ] Local transcription identifies low-confidence spans rather than fabricating words.
- [ ] DAXDA analysis cites transcript spans/timestamps and separates observation from inference.
- [ ] Independent reviewer verifies the evidence ledger and stop/permission paths.
