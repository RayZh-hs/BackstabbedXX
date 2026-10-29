"""Read saved Java block states for arena regression checks (stdlib only)."""
from functools import lru_cache
import gzip
from pathlib import Path
import struct
import zlib


def read_nbt(raw):
    pos = 0

    def take(n):
        nonlocal pos
        value = raw[pos:pos + n]
        pos += n
        if len(value) != n:
            raise ValueError("Truncated NBT")
        return value

    def number(fmt):
        return struct.unpack(">" + fmt, take(struct.calcsize(fmt)))[0]

    def string():
        return take(number("H")).decode("utf-8", errors="replace")

    def payload(kind):
        if kind in (1, 2, 3, 4, 5, 6):
            return number({1: "b", 2: "h", 3: "i", 4: "q", 5: "f", 6: "d"}[kind])
        if kind == 8:
            return string()
        if kind == 9:
            subtype, count = number("B"), number("i")
            return [payload(subtype) for _ in range(count)]
        if kind == 10:
            result = {}
            while True:
                subtype = number("B")
                if not subtype:
                    return result
                key = string()
                result[key] = payload(subtype)
        if kind in (7, 11, 12):
            count = number("i")
            fmt = {7: "b", 11: "i", 12: "q"}[kind]
            size = struct.calcsize(fmt)
            return list(struct.unpack(">" + str(count) + fmt, take(count * size)))
        raise ValueError(f"Unknown NBT tag {kind}")

    if number("B") != 10:
        raise ValueError("Expected NBT compound")
    string()
    return payload(10)


class World:
    def __init__(self, path):
        self.path = Path(path)

    @lru_cache(maxsize=16)
    def region(self, rx, rz):
        path = self.path / "region" / f"r.{rx}.{rz}.mca"
        return path.read_bytes() if path.exists() else b""

    @lru_cache(maxsize=2048)
    def chunk(self, cx, cz):
        raw = self.region(cx // 32, cz // 32)
        if not raw:
            return {}
        slot = cx % 32 + cz % 32 * 32
        entry = int.from_bytes(raw[slot * 4:slot * 4 + 4], "big")
        if not entry:
            return {}
        offset = (entry >> 8) * 4096
        length = int.from_bytes(raw[offset:offset + 4], "big")
        codec = raw[offset + 4]
        body = raw[offset + 5:offset + 4 + length]
        if codec == 1:
            body = gzip.decompress(body)
        elif codec == 2:
            body = zlib.decompress(body)
        elif codec != 3:
            raise ValueError(f"Unsupported region codec {codec}")
        return read_nbt(body)

    @lru_cache(maxsize=4096)
    def section(self, cx, sy, cz):
        return next((s.get("block_states", {}) for s in self.chunk(cx, cz).get("sections", [])
                     if s["Y"] == sy), {})

    def block(self, x, y, z):
        states = self.section(x // 16, y // 16, z // 16)
        palette = states.get("palette", [{"Name": "minecraft:air"}])
        if len(palette) == 1:
            return palette[0]
        bits = max(4, (len(palette) - 1).bit_length())
        per = 64 // bits
        index = (x % 16) + (z % 16) * 16 + (y % 16) * 256
        return palette[(states["data"][index // per] >> ((index % per) * bits)) & ((1 << bits) - 1)]


def in_region(predicate, point):
    kind = predicate["condition"].removeprefix("minecraft:")
    if kind == "any_of":
        return any(in_region(term, point) for term in predicate["terms"])
    if kind == "all_of":
        return all(in_region(term, point) for term in predicate["terms"])
    if kind == "inverted":
        return not in_region(predicate["term"], point)
    if kind != "location_check":
        raise ValueError(f"Unsupported geometry predicate {kind}")
    location = predicate["predicate"]
    if location.get("dimension", "minecraft:overworld") != "minecraft:overworld":
        return False
    return all(bounds.get("min", float("-inf")) <= value <= bounds.get("max", float("inf"))
               for axis, value in zip("xyz", point)
               for bounds in [location.get("position", {}).get(axis, {})])
