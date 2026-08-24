# DAXDA-o V5.2 External Rebuild Package

## Purpose

This package is designed for an outside reviewer to determine whether the DAXDA-o V5.2
software and its existing internal benchmark can be rebuilt and reproduced on a separate
computer.

A successful rebuild supports **reproducibility**. It does **not**, by itself, establish
independent validation, real-world safety, or deployment readiness.

## Required source artifacts

Before sending this package, Nicole must place the following original files into the
`SOURCE_FILES/` folder:

1. `daxda_engine_v5_2.py`
2. `build_v5_2_hidden_dataset.py`
3. `daxda_v5_2_hidden_test.json`
4. `run_v5_2_hidden_audit.py`
5. `daxda_v5_2_preregistered_manifest.json`

The package currently contains the verification framework and expected hashes, but not
those source artifacts because they were not included in the uploaded material used to
create this handoff.

## Reviewer sequence

1. Read `REVIEWER_INSTRUCTIONS.md`.
2. Install Python and an IDE or terminal environment.
3. Copy the five source artifacts into `SOURCE_FILES/`.
4. Run `python verify_package.py`.
5. Create an isolated virtual environment.
6. Install only dependencies required by the source.
7. Run the benchmark exactly as documented.
8. Save unedited terminal output in `RESULTS/raw_terminal_output.txt`.
9. Complete `RESULTS/reviewer_report.md`.
10. Return the entire folder as a ZIP archive.

## Decision labels

- **REPRODUCED:** Hashes match and the documented run completes with materially matching results.
- **PARTIALLY REPRODUCED:** The system builds, but results differ or some steps fail.
- **NOT REPRODUCED:** The system cannot be rebuilt or the core results cannot be obtained.
- **NOT ASSESSABLE:** Required artifacts, dependencies, or instructions are missing.

Do not replace these labels with “validated,” “certified,” or “production-ready.”
