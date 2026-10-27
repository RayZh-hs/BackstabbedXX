"""Stage a disposable singleplayer world and build its local-only NeoForge helper."""

from contextlib import contextmanager
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile


WORLD_NAME = "Backstabbed ++! by NorbMinecraft and Bagel Buddies"
HELPER_NAME = "backstabbed-local.jar"


@contextmanager
def local_game_directory(root):
    source = root / ".minecraft"
    world = source / "saves" / WORLD_NAME
    if not (world / "level.dat").is_file():
        raise SystemExit(f"Playtest world is missing: {world}")
    dev = root / "dev"
    dev.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="local-playtest-", dir=dev) as temporary:
        game = Path(temporary)
        # Copy settings and mods so game writes never reach the working copy.
        for name in ("config", "mods"):
            if (source / name).is_dir():
                shutil.copytree(source / name, game / name)
        if (source / "options.txt").is_file():
            shutil.copyfile(source / "options.txt", game / "options.txt")
        shutil.copytree(source / "resourcepacks", game / "resourcepacks")
        destination = game / "saves" / WORLD_NAME
        shutil.copytree(world, destination, ignore=shutil.ignore_patterns("session.lock"))
        (destination / ".backstabbed-local").touch()
        yield game


def build_helper(root, runtime, java, game, minecraft, neoforge):
    """Compile after PortableMC installs the game's pinned dependencies and JDK."""
    source = root / "scripts/local_playtest/LocalPlaytest.java"
    # NeoForge's patched classes must precede the original Minecraft classes.
    library = runtime / "libraries/net/neoforged/neoforge" / neoforge
    patched = library / f"neoforge-{neoforge}-client.jar"
    universal = library / f"neoforge-{neoforge}-universal.jar"
    if not patched.is_file() or not universal.is_file():
        raise SystemExit(f"NeoForge compile dependencies are missing from {library}")
    jars = [patched, universal] + sorted(
        path for path in (runtime / "libraries").rglob("*.jar")
        if path not in (patched, universal)
    )
    compiler = Path(java).parent / ("javac.exe" if os.name == "nt" else "javac")
    if not compiler.is_file():
        raise SystemExit(f"Local playtesting requires a Java 21 JDK (javac missing beside {java})")
    metadata = f'''modLoader="javafml"
loaderVersion="[4,)"
license="All Rights Reserved"
[[mods]]
modId="backstabbed_local"
version="1.0.0"
displayName="Backstabbed Local Playtest"
description="Idle players for disposable local playtests."
[[dependencies.backstabbed_local]]
modId="neoforge"
type="required"
versionRange="[{neoforge}]"
side="BOTH"
[[dependencies.backstabbed_local]]
modId="minecraft"
type="required"
versionRange="[{minecraft}]"
side="BOTH"
'''
    fingerprint = hashlib.sha256(source.read_bytes() + metadata.encode()).hexdigest()
    cache = root / "dev/local-playtest-helper" / fingerprint
    output = cache / HELPER_NAME
    if not output.is_file():
        cache.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=cache) as temporary:
            classes = Path(temporary)
            print("Building local playtest helper…", flush=True)
            subprocess.run([
                str(compiler), "--release", "21", "-proc:none",
                "-classpath", os.pathsep.join(str(path) for path in jars),
                "-d", str(classes), str(source),
            ], check=True)
            pending = classes / HELPER_NAME
            with zipfile.ZipFile(pending, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("META-INF/neoforge.mods.toml", metadata)
                for path in sorted(classes.rglob("*.class")):
                    archive.write(path, path.relative_to(classes).as_posix())
            pending.replace(output)
    (game / "mods").mkdir(exist_ok=True)
    shutil.copyfile(output, game / "mods" / HELPER_NAME)
