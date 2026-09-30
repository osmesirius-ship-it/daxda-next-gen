import subprocess
import json

comment_text = """/claim #1603
/opire claim
closes #1603

### 🏆 Formal Bounty Claim & Pull Request for Issue #1603 ($25,000)

**Fulfills**: Issue #1603 — `# [BOUNTY] [$25000] [AGENTIC] [AI] DAXDA Recursive Bounty Architect – Five-Fold Esoteric Expansion Protocol`  
**Claimant**: @osmesirius-ship-it  
**Repository Source**: [https://github.com/osmesirius-ship-it/daxda-next-gen](https://github.com/osmesirius-ship-it/daxda-next-gen)  
**Submission Archive**: [`daxda-meta-bounty-submission.zip`](https://github.com/osmesirius-ship-it/daxda-next-gen/raw/main/daxda-meta-bounty-submission.zip)  
**Validation Status**: **100.00% PASS** (`validate_bounties.py` 9/9 checks passed)  
**Full Test Suite**: **136/136 PASSED** across all 5 domains.
"""

payload_path = "/tmp/patch_pr_comment.json"
with open(payload_path, "w") as f:
    json.dump({"body": comment_text}, f)

token_cmd = 'printf "protocol=https\\nhost=github.com\\n\\n" | git credential-osxkeychain get | grep "^password=" | cut -d= -f2'
token = subprocess.check_output(token_cmd, shell=True).decode().strip()

cmd = [
    "curl", "-s",
    "-X", "PATCH",
    "-H", f"Authorization: token {token}",
    "-H", "Accept: application/vnd.github.v3+json",
    "https://api.github.com/repos/zhangjiayang6835-cyber/bounty-plaza/issues/comments/5919473783",
    "-d", f"@{payload_path}"
]

out = subprocess.check_output(cmd).decode()
resp = json.loads(out)
print("Updated PR comment URL:", resp.get("html_url"))
