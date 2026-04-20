#!/bin/bash

# Navigate to the workspace directory
cd /home/openclaw/.openclaw/workspace/model-price-reference || exit 1

# Make sure we are clean and sync with remote
git reset --hard -q
git pull --rebase origin main -q

# Backup current files for comparison
cp azure.json azure_old.json 2>/dev/null || true
cp aws.json aws_old.json 2>/dev/null || true
cp gcp.json gcp_old.json 2>/dev/null || true

# Execute extraction scripts
python3 scripts/azure_generate.py
python3 scripts/aws_generate.py
python3 scripts/gcp_generate.py

# Validate generated JSON files
python3 scripts/validate_json.py || { echo "JSON validation failed!"; exit 1; }

# Compare prices and collect alerts
ALERTS=""
A1=$(python3 scripts/global_compare_and_alert.py azure_old.json azure.json 2>/dev/null)
A2=$(python3 scripts/global_compare_and_alert.py aws_old.json aws.json 2>/dev/null)
A3=$(python3 scripts/global_compare_and_alert.py gcp_old.json gcp.json 2>/dev/null)

if [ -n "$A1" ]; then ALERTS="$ALERTS\n\n$A1"; fi
if [ -n "$A2" ]; then ALERTS="$ALERTS\n\n$A2"; fi
if [ -n "$A3" ]; then ALERTS="$ALERTS\n\n$A3"; fi

# Clean up backups
rm -f *_old.json

# Update status file for GitHub confirmation
echo "{\"last_run\": \"$(date -u +'%Y-%m-%dT%H:%M:%SZ')\", \"status\": \"success\"}" > status.json

# Commit and push if there are JSON changes
if [[ -n $(git status -s | grep -E "\.json|CHANGELOG\.md") ]]; then
    git add .
    git commit -m "chore(prices): update daily prices and changelog" -q
    git pull --rebase -X theirs origin main -q
    git push origin main -q
fi

# Output alerts for OpenClaw to send to Telegram
if [ -n "$ALERTS" ]; then
    echo -e "$ALERTS"
else
    # Magic word to instruct OpenClaw not to send a message if nothing changed
    echo "NO_REPLY"
fi
