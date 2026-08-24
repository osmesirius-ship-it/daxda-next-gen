# Reviewer Instructions

## Scope

You are being asked to test whether DAXDA-o V5.2 can be rebuilt and whether its existing
internal regression results can be reproduced on a separate machine.

You are **not** being asked to endorse the system, assess ownership, certify security, or
confirm deployment readiness.

## Independence rules

- Perform the work on your own computer.
- Do not modify the source before the first run.
- Record every modification required to make the run work.
- Do not suppress failures, warnings, or unexpected outputs.
- Do not rely on screenshots supplied by the developer as evidence of your run.
- Preserve raw output and environment details.
- State any prior involvement you have had with DAXDA.

## Environment record

Record:

- reviewer identifier
- date and timezone
- operating system
- machine architecture
- Python version
- IDE or terminal used
- dependency versions
- commands executed
- source hashes
- errors and warnings
- final classification

## Rebuild procedure

### 1. Verify package integrity

From the package root:

```bash
python verify_package.py
```

Do not continue silently if any hash differs. Record the mismatch.

### 2. Create an isolated environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 3. Inspect dependencies

Review imports in the source. Install only required third-party packages. Record every
installation command. Do not assume an undeclared dependency is acceptable.

### 4. Run the audit

From `SOURCE_FILES/`, run:

```bash
python run_v5_2_hidden_audit.py
```

If the documented entry point differs, record exactly what was required.

### 5. Preserve evidence

Save:

- complete terminal output
- generated reports
- error logs
- hash verification output
- dependency list (`python -m pip freeze`)
- screenshots only as supplemental evidence

### 6. Complete the report

Use `RESULTS/reviewer_report.md`. Do not edit the expected-results section to make the
observed run appear closer.

## Optional stronger test

After completing the untouched rebuild, create a small set of fresh prompts that were not
supplied by Nicole and were not derived from the existing corpus. Keep them private until
after execution. Report those results separately as an exploratory external test.

That optional test is more informative than rebuilding alone, but it is still not a full
independent safety validation unless the protocol, labels, and scoring are independently
defined in advance.
