#!/usr/bin/env python3
"""Generate a concise release-note entry for every commit since the prior tag."""

import argparse
from pathlib import Path
import re
import subprocess

from build import release_version


ROOT = Path(__file__).resolve().parent.parent


def git(*args, check=True):
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=check,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )


def release_notes(tag, repo):
    if not tag.startswith("v"):
        raise ValueError("Release tags must start with v")
    version = release_version(tag)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+", repo):
        raise ValueError("Expected a GitHub repository in owner/name form")
    ref = f"refs/tags/{tag}"
    git("rev-parse", "--verify", ref + "^{commit}")
    previous = git("describe", "--tags", "--abbrev=0", "--match", "v[0-9]*", ref + "^", check=False)
    previous_tag = previous.stdout.strip() if previous.returncode == 0 else ""
    revision = f"{previous_tag}..{ref}" if previous_tag else ref
    commits = git("log", "--reverse", "--format=%H%x00%s", revision).stdout.splitlines()
    base = f"https://github.com/{repo}"
    lines = ["## Changes", ""]
    for commit in commits:
        sha, subject = commit.split("\0", 1)
        lines.append(f"- {subject} ([`{sha[:7]}`]({base}/commit/{sha}))")
    comparison = f"{base}/compare/{previous_tag}...{tag}" if previous_tag else f"{base}/commits/{tag}"
    lines.extend([
        "", f"**Full changelog:** [all changes]({comparison})", "",
        "## Downloads", "",
        "- **Players:** import `Backstabbed++.zip` into Prism Launcher.",
        "- **HMCL players:** import `Backstabbed++.mrpack` using Install Modpack. This avoids the MultiMC LWJGL metadata lookup.",
        f"- **Hosts:** also extract `Backstabbed++-map-v{version}.zip` into the saves directory, or use its world on a dedicated server.",
        "- `backstabbed-resource.zip` is the standalone resource pack; `SHA256SUMS` verifies the downloads.", "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag", help="Existing version tag, such as v1.1.1-alpha")
    parser.add_argument("--repo", required=True, help="GitHub owner/repository")
    args = parser.parse_args()
    print(release_notes(args.tag, args.repo), end="")


if __name__ == "__main__":
    main()
