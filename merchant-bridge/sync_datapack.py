#!/usr/bin/env python3
"""Install the reviewable merchant functions into the source world's datapack.

Preserve all other ZIP members, refuse a running source world, and detect
concurrent datapack updates. This does not edit saved blocks or entities.
"""
from contextlib import contextmanager
import fcntl
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent.parent
WORLD = ROOT / ".minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies"


@contextmanager
def stopped():
    lock = WORLD / "session.lock"
    if not lock.exists():
        yield
        return
    with lock.open("r+b") as handle:
        try:
            fcntl.lockf(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise SystemExit("Close the source Minecraft world before updating its datapack.")
        try:
            yield
        finally:
            fcntl.lockf(handle, fcntl.LOCK_UN)


def sync():
    source = ROOT / "merchant-bridge/datapack"
    changes = {p.relative_to(source).as_posix(): p.read_bytes()
               for p in source.rglob("*") if p.is_file()}
    with stopped():
        path = WORLD / "datapacks/mcm.zip"
        before = path.read_bytes()
        with ZipFile(path) as archive:
            infos = archive.infolist()
            if len(infos) != len({i.filename for i in infos}):
                raise SystemExit("Datapack contains duplicate ZIP members; resolve before updating.")
            members = {i.filename: archive.read(i) for i in infos}
        # Add only the merchant lifecycle hook; keep the arena's independently
        # edited spawn points, decorations and activation logic intact.
        activation = "data/underwater_base/function/activate.mcfunction"
        hook = "function underwater_base:trader/spawn"
        lines = members[activation].decode().splitlines()
        if hook not in lines:
            changes[activation] = (members[activation].decode().rstrip() + "\n" + hook + "\n").encode()
        pending = path.with_suffix(".merchants-pending")
        try:
            with ZipFile(pending, "w", compression=ZIP_DEFLATED) as archive:
                for info in infos:
                    archive.writestr(info, changes.pop(info.filename, members[info.filename]))
                for name, content in sorted(changes.items()):
                    archive.writestr(name, content)
            if path.read_bytes() != before:
                raise SystemExit("Datapack changed concurrently; no update was applied.")
            pending.replace(path)
        finally:
            pending.unlink(missing_ok=True)
    print("Merchant datapack members synchronized; all other entries preserved.")


if __name__ == "__main__":
    sync()
