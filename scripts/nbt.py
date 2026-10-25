"""Update Data.LevelName in a Java level.dat without rewriting other NBT tags."""

import gzip
import struct


class Reader:
    def __init__(self, data):
        self.data = data
        self.position = 0

    def read(self, size):
        if size < 0 or self.position + size > len(self.data):
            raise ValueError("Invalid or truncated NBT data")
        start = self.position
        self.position += size
        return self.data[start:self.position]

    def number(self, fmt):
        return struct.unpack(">" + fmt, self.read(struct.calcsize(">" + fmt)))[0]

    def string(self):
        return self.read(self.number("H"))

    def skip(self, kind):
        sizes = {1: 1, 2: 2, 3: 4, 4: 8, 5: 4, 6: 8}
        if kind in sizes:
            self.read(sizes[kind])
        elif kind in (7, 11, 12):
            self.read(self.number("i") * {7: 1, 11: 4, 12: 8}[kind])
        elif kind == 8:
            self.string()
        elif kind == 9:
            subtype, count = self.number("B"), self.number("i")
            if count < 0 or (subtype == 0 and count):
                raise ValueError("Invalid NBT list")
            for _ in range(count):
                self.skip(subtype)
        elif kind == 10:
            while True:
                subtype = self.number("B")
                if subtype == 0:
                    break
                self.string()
                self.skip(subtype)
        else:
            raise ValueError(f"Unknown NBT tag type: {kind}")

    def find(self, name, expected_kind):
        while True:
            kind = self.number("B")
            if kind == 0:
                raise ValueError(f"Missing NBT tag: {name.decode()}")
            key = self.string()
            if key == name:
                if kind != expected_kind:
                    raise ValueError(f"Unexpected NBT tag type for {name.decode()}")
                return
            self.skip(kind)


def level_name_span(content):
    data = gzip.decompress(content)
    reader = Reader(data)
    if reader.number("B") != 10:
        raise ValueError("Expected a compound NBT root")
    reader.string()
    reader.find(b"Data", 10)
    reader.find(b"LevelName", 8)
    start = reader.position
    reader.string()
    return data, start, reader.position


def level_name(content):
    data, start, end = level_name_span(content)
    return data[start + 2:end].decode("utf-8")


def rename_level(content, name):
    data, start, end = level_name_span(content)
    encoded = name.encode("utf-8")
    replacement = struct.pack(">H", len(encoded)) + encoded
    return gzip.compress(data[:start] + replacement + data[end:], mtime=0)
