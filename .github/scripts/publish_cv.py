"""Publish PDFs from a disposable Actions checkout, without losing racing builds."""

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import time
from zoneinfo import ZoneInfo


def git(*args, check=True):
    return subprocess.run(
        ["git", *args], check=check, text=True, capture_output=True
    )


def ancestor(older, newer):
    return git("merge-base", "--is-ancestor", older, newer, check=False).returncode == 0


def should_replace(previous, source, branch_head):
    """A late-finishing older run must never replace a newer successful build."""
    if previous == source or not ancestor(source, branch_head):
        return False
    if not previous or not ancestor(previous, branch_head):
        return True
    return ancestor(previous, source)


def publish(pdf_path, source, branch):
    # Read everything needed from this build before switching to the current branch.
    pdf = Path(pdf_path).read_bytes()
    if not pdf.startswith(b"%PDF-"):
        raise ValueError("The compilation output is not a PDF")
    source = git("rev-parse", "--verify", "--end-of-options", f"{source}^{{commit}}").stdout.strip()
    committed = git("show", "-s", "--format=%cI", source).stdout.strip()
    local_time = datetime.fromisoformat(committed).astimezone(ZoneInfo("America/Chicago"))
    date = local_time.strftime("%Y%m%d")
    daily = Path(f"history/YangZhao_CV_{date}.pdf")
    latest = Path("YangZhao_CV.pdf")
    index = Path("history/build-index.json")
    git("check-ref-format", f"refs/heads/{branch}")
    git("config", "user.name", "github-actions[bot]")
    git("config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")

    for attempt in range(5):
        git("fetch", "origin", f"refs/heads/{branch}")
        head = git("rev-parse", "FETCH_HEAD").stdout.strip()
        # This script only runs in a disposable CI checkout, never the user's workspace.
        git("checkout", "--force", "-B", "cv-pdf-publish", head)
        state = json.loads(index.read_text()) if index.exists() else {"latest": None, "daily": {}}
        state["timezone"] = "America/Chicago"
        daily.parent.mkdir(exist_ok=True)
        if should_replace(state["daily"].get(date), source, head):
            daily.write_bytes(pdf)
            state["daily"][date] = source
        if should_replace(state["latest"], source, head):
            latest.write_bytes(pdf)
            state["latest"] = source
        index.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
        paths = [daily, latest, index]
        git("add", "--", *(str(path) for path in paths if path.exists()))
        if git("diff", "--cached", "--quiet", check=False).returncode == 0:
            print(f"Revision {source[:12]} has no newer PDFs to publish; no duplicate commit.")
            return
        git("commit", "-m", f"Update compiled CV for {source[:12]} [skip ci]")
        pushed = git("push", "origin", f"HEAD:refs/heads/{branch}", check=False)
        if pushed.returncode == 0:
            message = f"Published daily backup {daily}; latest and daily PDFs reflect the newest successful source revision."
            print(message)
            summary = os.environ.get("GITHUB_STEP_SUMMARY")
            if summary:
                with open(summary, "a") as stream:
                    stream.write(f"{message}\n\nSource commit: `{source}`\n")
            return
        if attempt == 4:
            raise RuntimeError(f"Could not publish PDFs after five attempts:\n{pushed.stderr}")
        time.sleep(attempt + 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--branch", default="main")
    args = parser.parse_args()
    if os.environ.get("GITHUB_ACTIONS") != "true":
        parser.error("Run this publisher only in a disposable GitHub Actions checkout")
    publish(args.pdf, args.source, args.branch)


if __name__ == "__main__":
    main()
