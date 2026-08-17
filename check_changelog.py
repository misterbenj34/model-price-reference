import os
import subprocess

repo_path = "/home/hermes/workspace/model-price-reference"
state_file = os.path.join(repo_path, ".last_commit")

os.chdir(repo_path)
subprocess.run(["git", "fetch"], check=True)
current_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()

last_commit = ""
if os.path.exists(state_file):
    with open(state_file, "r") as f:
        last_commit = f.read().strip()

print(f"Last checked commit: {last_commit}")
print(f"Current commit: {current_commit}")

if current_commit == last_commit:
    print("NO_NEW_CHANGES")
else:
    # Get changes in CHANGELOG.md between last_commit and current_commit
    if last_commit:
        diff = subprocess.check_output(["git", "diff", last_commit, current_commit, "--", "CHANGELOG.md"]).decode("utf-8")
    else:
        # Just show the top lines of CHANGELOG.md or git log
        diff = subprocess.check_output(["git", "log", "-n", "1", "-p", "--", "CHANGELOG.md"]).decode("utf-8")
    print("CHANGELOG_DIFF:")
    print(diff)
    with open(state_file, "w") as f:
        f.write(current_commit)
