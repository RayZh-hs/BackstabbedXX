#!/usr/bin/env python3
"""Compile the server-side merchant bridge with the launcher's pinned NeoForge JDK/libs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent
NAME = "backstabbed-merchants-1.0.0.jar"
METADATA = '''modLoader="javafml"
loaderVersion="[4,)"
license="All Rights Reserved"
[[mods]]
modId="backstabbed_merchants"
version="1.0.0"
displayName="Backstabbed Arena Merchants"
description="Vanilla trading screens for the arena panda and diving-suit zombie. Server-side only."
[[dependencies.backstabbed_merchants]]
modId="neoforge"
type="required"
versionRange="[21.4.158,21.5)"
side="BOTH"
[[dependencies.backstabbed_merchants]]
modId="minecraft"
type="required"
versionRange="[1.21.4]"
side="BOTH"
'''


def build(runtime):
    lib = runtime / "libraries/net/neoforged/neoforge/21.4.158"
    priority = [lib / f"neoforge-21.4.158-{kind}.jar" for kind in ("client", "universal")]
    compiler = runtime / "jvm/java-runtime-delta/bin/javac"
    if not compiler.is_file() or not all(p.is_file() for p in priority):
        raise SystemExit("Run make launch once to install Java 21 and the pinned NeoForge dependencies.")
    jars = priority + sorted(p for p in (runtime / "libraries").rglob("*.jar") if p not in priority)
    output = ROOT / ".minecraft/mods" / NAME
    with tempfile.TemporaryDirectory() as temporary:
        classes = Path(temporary)
        result = subprocess.run([str(compiler), "--release", "21", "-proc:none", "-classpath",
                        os.pathsep.join(map(str, jars)), "-d", str(classes),
                        *map(str, (ROOT / "merchant-bridge/src").rglob("*.java"))], check=False)
        if result.returncode:
            raise SystemExit("Merchant bridge compilation failed.")
        pending = output.with_suffix(".pending")
        with zipfile.ZipFile(pending, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            entries = {"META-INF/neoforge.mods.toml": METADATA.encode()}
            entries["backstabbed-merchants-build.json"] = json.dumps({
                "minecraft": "1.21.4", "neoforge": "21.4.158",
                "sources": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted((ROOT / "merchant-bridge/src").rglob("*.java"))},
            }, sort_keys=True).encode()
            entries.update({p.relative_to(classes).as_posix(): p.read_bytes() for p in classes.rglob("*.class")})
            for name, data in sorted(entries.items()):
                entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, data, compress_type=zipfile.ZIP_DEFLATED)
        pending.replace(output)
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, default=ROOT / "dev/launcher")
    build(parser.parse_args().runtime.resolve())
