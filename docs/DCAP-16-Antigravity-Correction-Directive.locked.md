# DCAP-16 correction directive — evidence-bound lock

**Status:** `DRAFT — PROPOSED FOR BENCHMARKING`  
**Release state:** `HOLD`  
**Scope:** DCAP design specification only. This document does not authorize deployment, identity resolution, clinical use, or modification of frozen v11.4.

## Locked findings

1. DCAP may record a candidate measurement or event timestamp. It does **not** establish a person's identity, metaphysical consciousness entry, or any other conclusion not supported by the supplied evidence.
2. Names for unnamed individuals must never be guessed or inferred from incomplete context. An identification may be reported only when authorized, reliable records explicitly link the individual to the name and that linkage is independently verified.
3. As of this repository review, no DCAP implementation, DCAP event-timestamp runner, or frozen-v11.4 DCAP adapter was found. Therefore no claim may state that Daxda is currently executing DCAP timestamps or that frozen v11.4 already performs DCAP checks.
4. The permitted v11.4 wording is: **“Designed for evaluation through a future external adapter governed by frozen v11.4.”** Frozen v11.4 remains unchanged.
5. DCAP evidence is tamper-evident only when a defined canonical serialization, signing procedure, verifier, signer/public-key identity, and retained source artifacts exist. A hash alone proves neither physical immutability nor reconstructability.

## Mandatory correction gate

The following source requirements remain mandatory before a DCAP record can be certified for its selected profile:

1. Use signed integer seconds plus integer fractional units; do not represent an exact atomic time with a floating-point value.
2. Retain accumulated proper time, worldline, clock identity, and the relativistic-correction model.
3. Store TT, TDB, and TCB separately with their transformation model and constants.
4. Preserve ephemeris vectors, units, epoch, time scale, kernel files, and hashes. Use the appropriate long-horizon profile (including the DE441 limitation disclosure where selected).
5. Archive the IANA TZDB release, zone identifier, source notes, and civil-time uncertainty; retain the applicable leap-second table and its hash.
6. Implement and retain the promised 16-dimensional covariance representation; two scalar error terms are not an equivalent substitute.
7. When pulsars are used, retain raw TOA, observatory position, receiver frequency, dispersion model, clock corrections, timing solution, and ephemeris. A residual alone is not an independent timestamp.
8. Keep evidence records and referee verdicts as separately signed objects. Define canonical serialization, field order, number encoding, Unicode normalization, signed byte range, and Ed25519 verification steps.
9. Do not claim that a ZK proof establishes the truth of sensor input or a timestamp. It can prove only the specified computation over the committed inputs.
10. Apply a profile-specific schema: `DCAP-CIVIL`, `DCAP-METROLOGICAL`, `DCAP-ASTRONOMICAL`, or `DCAP-RELATIVISTIC`. Pulsar evidence is not a default requirement for ordinary civil records.

## Consciousness-study boundary

DCAP establishes when and where a measurement was taken, not what that measurement means. Each proposed event boundary must retain synchronized EEG, cerebral oxygenation, autonomic data, raw-data and calibration hashes, first-breath/emergence/cord-clamping markers, preregistered change-point criteria, medical and environmental confounders, and uncertainty.

The only permitted finding after independent reproduction is:

> `Reproducible measured state transition detected at t* ± δt; metaphysical interpretation unverified.`

Block any claim that “consciousness entered” unless independent experiments show the transition uniquely tracks consciousness rather than plausible confounders such as breathing, oxygenation, medication, sensory exposure, or arousal.

## Certification hold

No v1.0 certification or frozen-v11.4 conformance claim is permitted until all of the following are supplied and independently reproduced:

- an executable DCAP validator and canonical serializer;
- a time-scale conversion engine and signature verifier;
- a separate external v11.4 adapter, with the frozen core unchanged;
- profile-specific fixtures, test vectors, negative/tamper tests, and execution receipts;
- retained source artifacts sufficient for reconstruction; and
- independent verification of any identity linkage or scientific conclusion.

Until then, the final characterization is: **strong architecture; incomplete implementation.**

## Daxda governance record

- Source directive SHA-256: `9208148fd626e765be796ebe849adee922edbac9ce67f2d0897c63bd9f8d7c78`
- Daxda V10 analysis mode: 16 layers, 886 operations, no external actions authorized
- Daxda governance disposition: `PASS` for this bounded correction analysis; this is **not** a substantive implementation certification
- Daxda audit SHA-256: `b25765f11b24ab1978f29ac1703600c56d6e3956510b495d939a5d5316c35ab8`
- Daxda release receipt SHA-256: `39543fcf01508f36d2f4984dee79f24a6d990465bc64258deb4d808df8bc6fea`

This lock is tamper-evident only when the file's own recorded digest and the cited input/audit receipts are verified together.
