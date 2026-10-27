"""Lossless Anvil chunk copying and isolated Java 1.21.4 editor saves."""

from contextlib import contextmanager
import copy
from io import BytesIO
import json
import math
from pathlib import Path
import struct
import time
import zlib

import nbtlib as nbt

DATA_VERSION = 4189
_HELD_LOCKS = set()


class WorldOpenError(ValueError):
    """A Minecraft process still holds the world's session.lock."""


@contextmanager
def stopped(world):
    """Java FileLock uses POSIX record locks, not flock. Never truncate its file."""
    import fcntl

    path = Path(world).resolve() / "session.lock"
    # POSIX locks belong to the process. Opening/closing a second descriptor for
    # the same file could release an outer lock, so nested operations reuse it.
    if path in _HELD_LOCKS:
        yield
        return
    if not path.exists():
        yield
        return
    with path.open("r+b") as handle:
        try:
            fcntl.lockf(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise WorldOpenError(f"Close this Minecraft world first: {world}") from error
        _HELD_LOCKS.add(path)
        try:
            yield
        finally:
            _HELD_LOCKS.remove(path)
            fcntl.lockf(handle, fcntl.LOCK_UN)


def read_region(path):
    """Return slot -> (timestamp, uncompressed NBT); reject unsupported formats."""
    if not path.exists():
        return {}
    raw = path.read_bytes()
    # Minecraft creates zero-length entity/POI regions before their first save.
    if not raw:
        return {}
    if len(raw) < 8192:
        raise ValueError(f"Truncated region: {path}")
    result = {}
    for slot in range(1024):
        location = int.from_bytes(raw[slot * 4:slot * 4 + 4], "big")
        if not location:
            continue
        start, sectors = (location >> 8) * 4096, location & 255
        if start < 8192 or start + sectors * 4096 > len(raw):
            raise ValueError(f"Invalid chunk location in {path}, slot {slot}")
        size = int.from_bytes(raw[start:start + 4], "big")
        if size < 1 or size + 4 > sectors * 4096:
            raise ValueError(f"Invalid chunk length in {path}, slot {slot}")
        codec = raw[start + 4]
        payload = raw[start + 5:start + 4 + size]
        if codec == 1:
            import gzip
            payload = gzip.decompress(payload)
        elif codec == 2:
            payload = zlib.decompress(payload)
        elif codec != 3:
            raise ValueError(f"Unsupported chunk compression {codec} in {path}; convert to vanilla 1.21.4 first")
        result[slot] = (int.from_bytes(raw[4096 + slot * 4:4100 + slot * 4], "big"), payload)
    return result


def write_region(path, chunks):
    header, bodies, sector = bytearray(8192), [], 2
    for slot, (stamp, payload) in sorted(chunks.items()):
        packed = zlib.compress(payload)
        body = struct.pack(">I", len(packed) + 1) + b"\x02" + packed
        count = math.ceil(len(body) / 4096)
        if count > 255:
            raise ValueError("External oversized chunks are not supported")
        header[slot * 4:slot * 4 + 4] = ((sector << 8) | count).to_bytes(4, "big")
        header[4096 + slot * 4:4100 + slot * 4] = int(stamp).to_bytes(4, "big")
        bodies.append(body.ljust(count * 4096, b"\0"))
        sector += count
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".pending")
    temporary.write_bytes(bytes(header) + b"".join(bodies))
    temporary.replace(path)


def encode(tag):
    stream = BytesIO()
    tag.write(stream)
    return stream.getvalue()


def footprint(bounds):
    """Inclusive block bounds -> region filenames and selected chunk slots."""
    result = {}
    for x in range(math.floor(bounds[0] / 16), math.floor(bounds[2] / 16) + 1):
        for z in range(math.floor(bounds[1] / 16), math.floor(bounds[3] / 16) + 1):
            result.setdefault(f"r.{x // 32}.{z // 32}.mca", set()).add(x % 32 + z % 32 * 32)
    return result


def copy_chunks(source, target, bounds, *, merge=False):
    """Keep NBT intact, including block entities, lights, POI and decorations.

    Extraction deliberately copies whole chunks at their original coordinates.
    Runtime/editor entities are excluded; editor overlays never enter the source.
    """
    count = 0
    for folder in ("region", "entities", "poi"):
        for filename, slots in footprint(bounds).items():
            original = read_region(source / folder / filename)
            destination = read_region(target / folder / filename) if merge else {}
            for slot in slots:
                destination.pop(slot, None)
                if slot not in original:
                    continue
                stamp, payload = original[slot]
                tag = nbt.File.parse(BytesIO(payload))
                version = int(tag.get("DataVersion", 0))
                if version > DATA_VERSION:
                    raise ValueError(f"Chunk DataVersion {version} is newer than Minecraft 1.21.4")
                if folder == "entities":
                    def keep(entity):
                        tags = set(map(str, entity.get("Tags", [])))
                        return not (tags & {"MapEntity", "PlayerSpawn", "ScrapSpawn", "SpectatorSpawn"}
                                    or any(t.startswith("bbe.") for t in tags))
                    tag["Entities"] = nbt.List[nbt.Compound](e for e in tag.get("Entities", []) if keep(e))
                    payload = encode(tag)
                if folder == "region":
                    count += 1
                destination[slot] = stamp, payload
            if destination:
                write_region(target / folder / filename, destination)
            elif merge and (target / folder / filename).exists():
                (target / folder / filename).unlink()
    return count


def create_level(source, target, title, position):
    level = copy.deepcopy(nbt.load(source / "level.dat"))
    data = level["Data"]
    version = int(data["DataVersion"])
    if not 2860 <= version <= DATA_VERSION:
        raise ValueError("Use a Java 1.18–1.21.4 source save; this tool does not convert world versions")
    for key in ("Player", "CustomBossEvents", "ScheduledEvents"):
        data.pop(key, None)
    data["LevelName"] = nbt.String(title)
    data["GameType"] = nbt.Int(1)
    data["allowCommands"] = nbt.Byte(1)
    data["hardcore"] = nbt.Byte(0)
    data["Difficulty"] = nbt.Byte(0)
    data["DifficultyLocked"] = nbt.Byte(0)
    data["LastPlayed"] = nbt.Long(int(time.time() * 1000))
    for axis, value in zip("XYZ", position):
        data["Spawn" + axis] = nbt.Int(math.floor(value))
    data["BorderCenterX"] = nbt.Double(0)
    data["BorderCenterZ"] = nbt.Double(0)
    data["BorderSize"] = data["BorderSizeLerpTarget"] = nbt.Double(59999968)
    data["BorderSizeLerpTime"] = nbt.Long(0)
    data["DataPacks"] = nbt.Compound({
        "Enabled": nbt.List[nbt.String](["vanilla", "file/backstabbed-editor"]),
        "Disabled": nbt.List[nbt.String]([]),
    })
    rules = data.setdefault("GameRules", nbt.Compound())
    for key, value in {
        "doDaylightCycle": "false", "doWeatherCycle": "false", "doMobSpawning": "false",
        "doPatrolSpawning": "false", "doTraderSpawning": "false", "doFireTick": "false",
        "randomTickSpeed": "0", "keepInventory": "true", "doImmediateRespawn": "true",
        "spawnRadius": "0", "commandBlockOutput": "false", "sendCommandFeedback": "false",
        "logAdminCommands": "false", "spawnChunkRadius": "0",
    }.items():
        rules[key] = nbt.String(value)
    settings = data["WorldGenSettings"]
    settings["generate_features"] = nbt.Byte(0)
    for dimension in settings["dimensions"].values():
        dimension["generator"] = nbt.parse_nbt(
            '{type:"minecraft:flat",settings:{biome:"minecraft:the_void",layers:[],lakes:0b,features:0b,structure_overrides:[]}}')
    target.mkdir(parents=True, exist_ok=True)
    level.save(target / "level.dat")


def saved_state(world):
    path = world / "data/command_storage_bbe.dat"
    if path.exists():
        contents = nbt.load(path)["data"]["contents"]
        if "session" in contents and "state" in contents["session"]:
            return json.loads(json.dumps(contents["session"]["state"].unpack(), default=lambda v: v.tolist()))
        raise ValueError(f"Editor storage is missing its state: {path}")
    return json.loads((world / ".backstabbed-editor-seed.json").read_text())
