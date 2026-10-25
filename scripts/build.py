#!/usr/bin/env python3
"""Build the resource pack and a Prism-compatible instance ZIP."""

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
RESOURCEPACK_NAME = "backstabbed-resource.zip"
RESOURCEPACK_SOURCE = ROOT / ".minecraft/resourcepacks/backstabbed-resource"


def write_zip(destination, files):
    """Replace an archive in full, so removed source files cannot linger."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(dir=destination.parent, suffix=".tmp")
    os.close(handle)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(temporary, "w") as archive:
            for name, source in sorted(files.items()):
                # Stable timestamps and permissions make identical builds reproducible.
                entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                entry.create_system = 3
                entry.external_attr = 0o100644 << 16
                archive.writestr(
                    entry,
                    source.read_bytes(),
                    compress_type=zipfile.ZIP_DEFLATED,
                    compresslevel=9,
                )
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Built {destination.relative_to(ROOT)} ({len(files)} files)")


def build_resourcepack():
    metadata = RESOURCEPACK_SOURCE / "pack.mcmeta"
    if not metadata.is_file() or not (RESOURCEPACK_SOURCE / "assets").is_dir():
        raise SystemExit(f"Resource-pack source is missing: {RESOURCEPACK_SOURCE}")
    json.loads(metadata.read_text(encoding="utf-8"))
    files = {
        path.relative_to(RESOURCEPACK_SOURCE).as_posix(): path
        for path in RESOURCEPACK_SOURCE.rglob("*")
        if path.is_file()
    }
    # Refresh the installed ZIP as well, so Prism exports use the latest edits.
    installed = RESOURCEPACK_SOURCE.parent / RESOURCEPACK_NAME
    write_zip(installed, files)
    DIST.mkdir(exist_ok=True)
    output = DIST / RESOURCEPACK_NAME
    shutil.copyfile(installed, output)
    print(f"Copied {output.relative_to(ROOT)}")
    return output


def build_pack(resourcepack):
    # Include tracked files and new, non-ignored files, even before the first commit.
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    blocked = {
        PurePosixPath(line)
        for line in (ROOT / ".packignore").read_text(encoding="utf-8").splitlines()
        if line
    }
    files = {}
    for raw_name in result.stdout.split(b"\0"):
        if not raw_name:
            continue
        name = os.fsdecode(raw_name)
        path = PurePosixPath(name)
        if name != "mmc-pack.json" and not name.startswith(".minecraft/"):
            continue
        if any(parent in blocked for parent in (path, *path.parents)):
            continue
        source = ROOT / name
        if source.is_file():
            files[name] = source
    if "mmc-pack.json" not in files:
        raise SystemExit("mmc-pack.json is missing or excluded from the build")
    # Use portable launcher settings instead of the developer's ignored instance.cfg.
    files["instance.cfg"] = ROOT / "instance.cfg.example"
    files[f".minecraft/resourcepacks/{RESOURCEPACK_NAME}"] = resourcepack
    write_zip(DIST / "Backstabbed++.zip", files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", choices=("pack", "resourcepack"))
    args = parser.parse_args()
    resourcepack = build_resourcepack()
    if args.target == "pack":
        build_pack(resourcepack)


if __name__ == "__main__":
    main()
