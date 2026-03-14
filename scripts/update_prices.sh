#!/bin/bash

# Navigate to the workspace directory
cd /home/openclaw/.openclaw/workspace/model-price-reference || exit 1

# Pull latest changes from remote
git pull origin main -q

# Backup current files for comparison
cp azure.json azure_old.json 2>/dev/null || true
cp aws.json aws_old.json 2>/dev/null || true
cp gcp.json gcp_old.json 2>/dev/null || true

# Execute extraction scripts
# Note: extract_azure.py requires Playwright implementation as noted in METHODOLOGY.md
# Uncomment when ready.
# python3 scripts/extract_azure.py
python3 scripts/generate_aws.py
python3 scripts/generate_gcp.py

# Compare prices and collect alerts
ALERTS=""
A1=$(python3 scripts/compare_and_alert.py azure_old.json azure.json 2>/dev/null)
A2=$(python3 scripts/compare_and_alert.py aws_old.json aws.json 2>/dev/null)
A3=$(python3 scripts/compare_and_alert.py gcp_old.json gcp.json 2>/dev/null)

if [ -n "$A1" ]; then ALERTS="$ALERTS\n\n$A1"; fi
if [ -n "$A2" ]; then ALERTS="$ALERTS\n\n$A2"; fi
if [ -n "$A3" ]; then ALERTS="$ALERTS\n\n$A3"; fi

# Clean up backups
rm -f *_old.json

# Commit and push if there are JSON changes
if [[ -n $(git status -s | grep "\.json") ]]; then
    git add .
    git commit -m "Automated daily price update" -q
    git push origin main -q
fi

# Output alerts for OpenClaw to send to Telegram
if [ -n "$ALERTS" ]; then
    echo -e "$ALERTS"
else
    # Magic word to instruct OpenClaw not to send a message if nothing changed
    echo "NO_REPLY"
fi