#!/usr/bin/env bash
# Open formal NIST AI 200-2 TEVV-Athlon Public Comment Submission draft in Apple Mail
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TXT_PATH="$(cd "${SCRIPT_DIR}/../docs/compliance" && pwd)/NIST_AI_200_2_TEVV_ATHLON_PUBLIC_COMMENT_OCTOBER_2026.txt"

if [ ! -f "${TXT_PATH}" ]; then
  echo "Error: Submission file not found at ${TXT_PATH}" >&2
  exit 1
fi

osascript -e '
on run argv
    set txtPath to POSIX file (item 1 of argv)
    set emailBody to (read txtPath as «class utf8»)
    tell application "Mail"
        set newMsg to make new outgoing message with properties {subject:"NIST AI 200-2: Public Comment on TEVV-Athlon Framework (Initial Public Draft)", content:emailBody, visible:true}
        tell newMsg
            make new to recipient with properties {address:"TEVV-Athlon@nist.gov"}
        end tell
        activate
    end tell
end run
' "${TXT_PATH}"

echo "Opened draft message in Apple Mail addressed to TEVV-Athlon@nist.gov."
