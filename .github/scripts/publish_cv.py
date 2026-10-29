"""Publish PDFs from a disposable Actions checkout, without losing racing builds."""

import argparse
import hashlib
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import time
import tempfile
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


def rendered_pages(pdf_path):
    """Compare all visible pages, ignoring PDF timestamps, IDs, and serialization."""
    with tempfile.TemporaryDirectory() as directory:
        prefix = Path(directory) / "page"
        subprocess.run(
            ["pdftoppm", "-r", "150", str(pdf_path), str(prefix)],
            check=True, capture_output=True, timeout=90,
        )
        pages = sorted(Path(directory).glob("page-*.ppm"))
        if not pages:
            raise ValueError("The compiled PDF has no rendered pages")
        return [hashlib.sha256(page.read_bytes()).digest() for page in pages]


def same_cv(candidate, previous):
    previous = Path(previous)
    if not previous.exists():
        return False
    if Path(candidate).read_bytes() == previous.read_bytes():
        return True
    return rendered_pages(candidate) == rendered_pages(previous)


def publish(pdf_path, source, branch):
    pdf_path = Path(pdf_path).resolve()
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
        # A no-change build deliberately leaves no ledger commit. Reject older
        # builds using source history so they cannot publish after such a build.
        newest_source = git(
            "log", "-1", "--format=%H", "--first-parent", head, "--", ".",
            ":(exclude)YangZhao_CV.pdf", ":(exclude)history",
        ).stdout.strip()
        if newest_source and not ancestor(newest_source, source):
            print("A newer source revision is on main; skipping this superseded build.")
            return
        if same_cv(pdf_path, latest):
            message = "CV pages are unchanged; skipping PDF upload, history backup, and commit."
            print(message)
            summary = os.environ.get("GITHUB_STEP_SUMMARY")
            if summary:
                with open(summary, "a") as stream:
                    stream.write(message + "\n")
            return
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
    parser.add_argument("--source")
    parser.add_argument("--compare-with", help="Compare visible pages without publishing")
    parser.add_argument("--branch", default="main")
    args = parser.parse_args()
    if args.compare_with:
        changed = not same_cv(args.pdf, args.compare_with)
        print(f"CV changed: {str(changed).lower()}")
        output = os.environ.get("GITHUB_OUTPUT")
        if output:
            with open(output, "a") as stream:
                stream.write(f"changed={str(changed).lower()}\n")
        return
    if not args.source:
        parser.error("--source is required when publishing")
    if os.environ.get("GITHUB_ACTIONS") != "true":
        parser.error("Run this publisher only in a disposable GitHub Actions checkout")
    publish(args.pdf, args.source, args.branch)


if __name__ == "__main__":
    main()
