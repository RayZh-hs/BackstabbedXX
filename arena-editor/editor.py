#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["nbtlib==2.0.4"]
# ///
"""Extract, launch, export and apply persistent Backstabbed++ arena sessions."""

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
import zipfile

import nbtlib as nbt

import pack
from world import WorldOpenError, copy_chunks, create_level, footprint, saved_state, stopped

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_WORLD = ROOT / ".minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies"
IDENTIFIER = re.compile(r"[a-z0-9_][a-z0-9_.-]*\Z")
NUMBER = r"-?(?:\d+(?:\.\d*)?|\.\d+)"
TRIPLE = rf"({NUMBER})\s+({NUMBER})\s+({NUMBER})"
COORD = rf"(?:{NUMBER}|~(?:{NUMBER})?)"
SPAWN = re.compile(rf"summon (?:minecraft:)?marker\s+({COORD})\s+({COORD})\s+({COORD})\s+(\{{.*\}})\s*$")
HELPER = re.compile(r"run function mcm:game/markers/(playerspawn|scrapspawn|spectatorspawn)\s*$")


def stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def digest(path):
    if not path.exists():
        return None
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def config(path):
    path = path.expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"Copy {HERE / 'config.example.json'} to {path} and set game_dir and launch_command")
    result = json.loads(path.read_text())
    for key in ("game_dir", "source_world", "launch_cwd"):
        value = result.get(key)
        if value:
            candidate = Path(os.path.expandvars(value)).expanduser()
            result[key] = (candidate if candidate.is_absolute() else path.parent / candidate).resolve()
    if "game_dir" not in result:
        raise ValueError("Local config must set game_dir to the chosen instance's .minecraft directory")
    result.setdefault("source_world", DEFAULT_WORLD)
    result.setdefault("launch_cwd", path.parent)
    return result


def archive_files(world):
    archive = world / "datapacks/mcm.zip"
    if not archive.exists():
        raise ValueError(f"Backstabbed++ datapack is missing: {archive}")
    with zipfile.ZipFile(archive) as handle:
        return {name: handle.read(name) for name in handle.namelist() if not name.endswith("/")}


def function_path(identifier):
    namespace, name = identifier.split(":", 1)
    return f"data/{namespace}/function/{name}.mcfunction"


def discover(files):
    """Use the voting table, not a duplicated hard-coded list of maps."""
    end = files["data/mcm/function/lobby/voting/end.mcfunction"].decode()
    result, boxes = {}, {}
    for line in end.splitlines():
        if line.lstrip().startswith("#"):
            continue
        tag = re.search(r"tag=SelectedMap,tag=([A-Za-z0-9_]+)", line)
        if not tag:
            continue
        tag = tag[1]
        force = re.search(r"forceload add (-?\d+) (-?\d+) (-?\d+) (-?\d+)", line)
        if force:
            a, b, c, d = map(int, force.groups())
            boxes.setdefault(tag, []).append([min(a, c), min(b, d), max(a, c), max(b, d)])
        activate = re.search(r"schedule function ([a-z0-9_:/.-]+)/activate", line)
        if activate:
            base = activate[1]
            arena = base.split("/")[-1] if "/" in base else base.split(":")[0]
            result[arena] = {"arena": arena, "tag": tag, "activation": base + "/activate"}
            if base.endswith(":"):
                result[arena]["activation"] = base + "activate"
        # Namespace-only identifiers have a colon before 'activate', not '/'.
        direct = re.search(r"schedule function ([a-z0-9_]+):activate", line)
        if direct:
            arena = direct[1]
            result[arena] = {"arena": arena, "tag": tag, "activation": arena + ":activate"}
    all_text = "\n".join(value.decode(errors="replace") for name, value in files.items()
                          if name.endswith(".mcfunction") and ("respawn_entities" in name or "/register." in name))
    for arena, spec in result.items():
        candidates = boxes.get(spec["tag"], [])
        if candidates:
            spec["bounds"] = [min(b[0] for b in candidates), min(b[1] for b in candidates),
                              max(b[2] for b in candidates), max(b[3] for b in candidates)]
        match = re.search(rf"tag={re.escape(spec['tag'])}\][^\n]* MapValues (\d+)", all_text)
        spec["map_id"] = int(match[1]) if match else None
        report_path = ROOT / "docs/arenas" / (arena + ".json")
        report = json.loads(report_path.read_text()) if report_path.exists() else {}
        if "scene_chunk_bounds" in report:
            xs, zs = report["scene_chunk_bounds"]["x"], report["scene_chunk_bounds"]["z"]
            spec["bounds"] = [xs[0] * 16, zs[0] * 16, xs[1] * 16 + 15, zs[1] * 16 + 15]
        spec["map_id"] = report.get("map_id", spec["map_id"])
        spec["title"] = report.get("title", arena.replace("_", " ").title())
        spec["provenance"] = {k: report[k] for k in ("creator", "source_url", "reuse_terms") if k in report}
    return result


def point_from_line(line):
    if line.lstrip().startswith("#"):
        return None
    if not SPAWN.search(line) and not HELPER.search(line):
        return None
    positioned = re.search(rf"\bpositioned {TRIPLE}", line)
    origin = list(map(float, positioned.groups())) if positioned else None
    rotated = re.search(rf"\brotated ({NUMBER}) ({NUMBER})", line)
    guard = ""
    if positioned:
        prefix = line[:positioned.start()].strip()
        if prefix != "execute":
            guard = prefix.removeprefix("execute ")
            if not re.fullmatch(r"if score \$[A-Za-z0-9_]+ CmdData matches -?\d+(?:\.\.-?\d+)?", guard):
                raise ValueError(f"Unsupported conditional spawn: {line}")
    extra = {"guard": guard} if guard else {}
    match = SPAWN.search(line)
    if match:
        value = nbt.parse_nbt(match[4])
        tags = set(map(str, value.get("Tags", [])))
        kinds = tags & {"PlayerSpawn", "ScrapSpawn", "SpectatorSpawn"}
        if not kinds:
            return None
        kind = "both" if {"PlayerSpawn", "ScrapSpawn"} <= kinds else (
            "player" if "PlayerSpawn" in kinds else "ammo" if "ScrapSpawn" in kinds else "spectator")
        rotation = value.get("Rotation", [0, 0])
        position = []
        for i, coordinate in enumerate(match.groups()[:3]):
            if coordinate.startswith("~"):
                if origin is None:
                    raise ValueError(f"Relative spawn without an absolute origin: {line}")
                position.append(origin[i] + float(coordinate[1:] or 0))
            else:
                position.append(float(coordinate))
        return dict(zip("xyz", position), kind=kind, yaw=float(rotation[0]), pitch=float(rotation[1]), **extra)
    match = HELPER.search(line.strip())
    if match and origin is not None:
        # The game's player helper creates a combined player + scrap marker.
        return dict(zip("xyz", origin),
                    kind={"playerspawn": "both", "scrapspawn": "ammo", "spectatorspawn": "spectator"}[match[1]],
                    yaw=float(rotated[1]) if rotated else 0.0, pitch=float(rotated[2]) if rotated else 0.0, **extra)
    return None


def predicate_boxes(value):
    """Convert an exact union of location boxes; refuse lossy approximations."""
    condition = value.get("condition", "").removeprefix("minecraft:")
    if condition == "any_of":
        return [box for term in value["terms"] for box in predicate_boxes(term)]
    if condition == "location_check":
        location = value["predicate"]
        if any(k in value for k in ("offsetX", "offsetY", "offsetZ")):
            raise ValueError("Offset location predicates need manual conversion")
    elif condition == "entity_properties" and value.get("entity") == "this":
        if set(value["predicate"]) != {"location"}:
            raise ValueError("Arena predicate contains non-location entity conditions")
        location = value["predicate"]["location"]
    else:
        raise ValueError(f"Arena predicate condition {condition!r} cannot be converted to editable boxes")
    if set(location) - {"dimension", "position"}:
        raise ValueError("Arena predicate contains non-box location conditions")
    if location.get("dimension", "minecraft:overworld") != "minecraft:overworld":
        raise ValueError("Only Overworld arena boxes can be imported")
    result = {"kind": "area", "mode": "keep_in", "action": "tp", "enabled": 1, "yaw": 0.0, "pitch": 0.0}
    for axis, default in zip("xyz", [(-29999984, 29999984), (-64, 319.999999), (-29999984, 29999984)]):
        interval = location.get("position", {}).get(axis, {})
        if isinstance(interval, (int, float)):
            interval = {"min": interval, "max": interval}
        lo, hi = interval.get("min", default[0]), interval.get("max", default[1])
        result[axis + "1"], result[axis + "2"] = float(lo), float(hi)
        result[axis] = (lo + hi) / 2
    return [result]


def seed_state(files, spec):
    previous = files.get(f"data/bbe_arena/editor/{spec['arena']}.json")
    if previous:
        return validate(json.loads(previous))
    activation = files[function_path(spec["activation"])].decode()
    objects = [p for line in activation.splitlines() if (p := point_from_line(line))]
    if not objects:
        raise ValueError("No recognizable spawn commands in activation; refusing an empty or partial spawn import")
    # Unknown spawn syntax must never disappear during an eventual apply.
    unknown = [line for line in activation.splitlines() if not line.lstrip().startswith("#")
               and re.search(r"PlayerSpawn|ScrapSpawn|SpectatorSpawn|mcm:game/markers/(?:player|scrap|spectator)spawn", line)
               and not point_from_line(line) and not line.strip().startswith(("kill ", "tag "))]
    if unknown:
        raise ValueError("Unsupported spawn commands need explicit conversion: " + "\n".join(unknown))
    player = next((p for p in objects if p["kind"] in ("player", "both")), objects[0])
    target = {**player, "kind": "return"}
    namespace = spec["arena"]
    for name in ("return_player", "return_to_arena"):
        text = files.get(f"data/{namespace}/function/{name}.mcfunction", b"").decode()
        match = re.search(rf"tp @s {TRIPLE}", text)
        if match:
            target.update(zip("xyz", map(float, match.groups())))
            break
    objects.append(target)
    predicate = files.get(f"data/{namespace}/predicate/arena.json")
    notes = []
    if predicate:
        objects.extend(predicate_boxes(json.loads(predicate)))
    else:
        notes.append("This arena has no arena.json predicate. Existing hard-coded mechanics are retained on apply; create editable boxes as needed.")
    report = ROOT / "docs/arenas" / (namespace + ".json")
    metadata = json.loads(report.read_text()) if report.exists() else {}
    enabled = int(bool(predicate) and metadata.get("boundary_teleport_enabled", True))
    for i, item in enumerate(objects, 1):
        item["id"] = i
    return {"schema": 1, "next_id": len(objects) + 1, "objects": objects,
            "boundary_enabled": enabled, "outside_action": "kill", "notes": notes}


def validate(state):
    if state.get("schema") != 1 or not isinstance(state.get("objects"), list):
        raise ValueError("Invalid editor state schema")
    if len(state["objects"]) > 5000:
        raise ValueError("Editor supports at most 5000 objects")
    if state.get("outside_action") not in ("tp", "kill") or state.get("boundary_enabled") not in (0, 1):
        raise ValueError("Invalid boundary settings")
    ids, counts = set(), Counter()
    for item in state["objects"]:
        identifier = item.get("id")
        if not isinstance(identifier, int) or identifier <= 0 or identifier in ids:
            raise ValueError("Object IDs must be unique positive integers")
        ids.add(identifier)
        kind = item.get("kind")
        if kind not in ("player", "ammo", "both", "spectator", "return", "area"):
            raise ValueError(f"Unknown object kind: {kind}")
        counts[kind] += 1
        if "guard" in item and not re.fullmatch(r"if score \$[A-Za-z0-9_]+ CmdData matches -?\d+(?:\.\.-?\d+)?", item["guard"]):
            raise ValueError("Invalid conditional spawn guard")
        for field in ("x", "y", "z", "yaw", "pitch"):
            if not isinstance(item.get(field), (int, float)) or not math.isfinite(item[field]):
                raise ValueError(f"Object {identifier} has an invalid {field}")
        if not -29999984 <= item["x"] <= 29999984 or not -29999984 <= item["z"] <= 29999984:
            raise ValueError("Object exceeds Minecraft's world limits")
        if kind == "area":
            if item.get("mode") not in ("keep_in", "keep_out") or item.get("action") not in ("tp", "kill") or item.get("enabled") not in (0, 1):
                raise ValueError(f"Object {identifier} has invalid constraint settings")
            for axis in "xyz":
                lo, hi = item.get(axis + "1"), item.get(axis + "2")
                if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in (lo, hi)) or lo > hi:
                    raise ValueError(f"Object {identifier} has invalid box bounds")
    if counts["return"] != 1 or counts["player"] + counts["both"] == 0:
        raise ValueError("Keep exactly one return point and at least one player spawn")
    if not isinstance(state.get("next_id"), int) or state["next_id"] <= max(ids, default=0):
        raise ValueError("next_id must exceed all existing IDs")
    return state


def source_hashes(source, bounds):
    names = ["datapacks/mcm.zip"] + [f"{folder}/{name}" for folder in ("region", "entities", "poi") for name in footprint(bounds)]
    return {name: digest(source / name) for name in names}


def prepare(settings, arena, bounds=None):
    source = settings["source_world"]
    if not IDENTIFIER.fullmatch(arena):
        raise ValueError("Arena name must contain only lowercase letters, numbers, underscores, dots or hyphens")
    target = settings["game_dir"] / "saves" / ("Backstabbed-Editor-" + arena)
    if target.exists():
        raise ValueError(f"Session already exists; launch it to resume, or choose another instance: {target}")
    with stopped(source):
        files = archive_files(source)
        registry = discover(files)
        if arena not in registry:
            raise ValueError(f"Unknown arena {arena!r}; use the list command")
        spec = registry[arena]
        bounds = bounds or spec.get("bounds")
        if not bounds or bounds[0] > bounds[2] or bounds[1] > bounds[3]:
            raise ValueError("Specify --bounds MIN_X MIN_Z MAX_X MAX_Z for this arena")
        if sum(map(len, footprint(bounds).values())) > 4096:
            raise ValueError("Extraction is limited to 4096 chunks; reduce --bounds")
        state = validate(seed_state(files, spec))
        for item in state["objects"]:
            if item["kind"] != "area" and not (bounds[0] // 16 * 16 <= item["x"] < (bounds[2] // 16 + 1) * 16
                                                and bounds[1] // 16 * 16 <= item["z"] < (bounds[3] // 16 + 1) * 16):
                raise ValueError(f"Spawn #{item['id']} is outside extraction bounds; widen --bounds")
        return_point = next(o for o in state["objects"] if o["kind"] == "return")
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".bbe-prepare-", dir=target.parent) as temporary:
            staging = Path(temporary) / target.name
            create_level(source, staging, "Arena Editor — " + spec["title"], [return_point[a] for a in "xyz"])
            count = copy_chunks(source, staging, bounds)
            if not count:
                raise ValueError("No source chunks in extraction bounds")
            pack.build(staging / "datapacks/backstabbed-editor", state)
            dump(staging / ".backstabbed-editor-seed.json", state)
            manifest = {"schema": 1, "created": stamp(), "source_world": str(source.resolve()),
                        "spec": spec, "bounds": bounds, "source_hashes": source_hashes(source, bounds)}
            dump(staging / ".backstabbed-editor.json", manifest)
            # Credits and license notices travel with the isolated arena.
            for name, contents in files.items():
                if name.startswith(f"data/{arena}/") and name.endswith(("credits.txt", "license-notice.txt")):
                    notice = staging / "attribution" / Path(name).name
                    notice.parent.mkdir(exist_ok=True)
                    notice.write_bytes(contents)
            staging.rename(target)
    print(f"Prepared {target}\nCopied {count} complete chunks; neighboring chunks generate as void.")
    print("Objects:", dict(Counter(o["kind"] for o in state["objects"])))
    print("Launch this session, then right-click the editor book or run /function bbe:menu.")
    for note in state["notes"]:
        print("Note:", note)
    return target


def session(settings, arena):
    if not IDENTIFIER.fullmatch(arena):
        raise ValueError("Invalid arena identifier")
    world = settings["game_dir"] / "saves" / ("Backstabbed-Editor-" + arena)
    if not (world / ".backstabbed-editor.json").is_file():
        raise ValueError(f"Prepare the arena first: {world}")
    return world


def launch_invocation(settings, world):
    command = settings.get("launch_command")
    if not isinstance(command, list) or not command or not all(isinstance(a, str) for a in command):
        raise ValueError("Set launch_command to a nonempty JSON array of arguments in the local config")
    replacements = {"{game_dir}": str(settings["game_dir"]), "{world_dir}": str(world),
                    "{world_name}": world.name, "{repo}": str(ROOT)}
    # Literal substitution preserves unrelated braces in JVM/launcher arguments.
    for placeholder, value in replacements.items():
        command = [argument.replace(placeholder, value) for argument in command]
    env = {**os.environ, "BBE_GAME_DIR": str(settings["game_dir"]), "BBE_WORLD_DIR": str(world), "BBE_WORLD_NAME": world.name}
    return command, env


def launch(settings, arena):
    world = session(settings, arena)
    with stopped(world):
        pass
    command, env = launch_invocation(settings, world)
    print(f"Open Singleplayer → {world.name}. Edits persist between launches.", flush=True)
    return subprocess.run(command, cwd=settings["launch_cwd"], env=env, check=False).returncode


def world_is_open(world):
    try:
        with stopped(world):
            return False
    except WorldOpenError:
        return True


def save_signature(world):
    """Detect a short editing session that starts and closes between polls."""
    result = []
    for path in (world / "level.dat", world / "session.lock"):
        try:
            info = path.stat()
            result.append((info.st_mtime_ns, info.st_size))
        except FileNotFoundError:
            result.append(None)
    return tuple(result)


def wait_for_edit_close(world, process, before):
    """Watch Java's lock, including launchers that detach from the game process."""
    opened = False
    while True:
        busy = world_is_open(world)
        if busy and not opened:
            print("Editor world opened. Save and Quit to Title when finished; this terminal will then offer to write it back.", flush=True)
            opened = True
        if opened and not busy:
            print("Editor world is closed.", flush=True)
            return process.poll() or 0
        code = process.poll()
        if code is not None and not opened:
            if code:
                return code
            if save_signature(world) != before:
                return 0
            # GUI launchers may exit before the game opens its save. A terminal
            # acknowledgement prevents treating that early return as completion.
            try:
                input(f"Launcher returned. Open {world.name}, finish editing, Save and Quit, then press Enter here (Ctrl-C cancels): ")
            except EOFError:
                print("No terminal input; the editor session is kept without applying changes.")
                return None
            while world_is_open(world):
                if not opened:
                    print("The editor world is still open; waiting for it to close…", flush=True)
                    opened = True
                time.sleep(0.5)
            return 0
        time.sleep(0.5)


def launch_for_edit(settings, arena):
    world = session(settings, arena)
    with stopped(world):
        pass
    command, env = launch_invocation(settings, world)
    before = save_signature(world)
    print(f"Launching {arena}. Open Singleplayer → Arena Editor — {arena.replace('_', ' ').title()} if your command does not select the world automatically.", flush=True)
    process = subprocess.Popen(command, cwd=settings["launch_cwd"], env=env)
    # Closing a world can leave the client/launcher running. Do not terminate it.
    return wait_for_edit_close(world, process, before)


def choose_arena(registry):
    choices = sorted(registry, key=lambda name: registry[name].get("map_id") or 999)
    print("Available arenas:")
    for number, name in enumerate(choices, 1):
        print(f"  {number:2}. {name:20} {registry[name]['title']}")
    while True:
        try:
            answer = input("Choose an arena by name or number (Enter cancels): ").strip()
        except EOFError:
            return None
        if not answer:
            return None
        if answer.isdecimal() and 1 <= int(answer) <= len(choices):
            return choices[int(answer) - 1]
        normalized = answer.casefold().replace(" ", "_")
        if normalized in registry:
            return normalized
        print("Unknown arena. Enter one of the listed names or numbers.")


def check_baseline(source, manifest):
    changed = [name for name, expected in manifest["source_hashes"].items() if digest(source / name) != expected]
    if changed:
        raise ValueError("Source changed since extraction; move the old editor save aside and prepare a fresh session. Conflicts: " + ", ".join(changed))


def edit(settings, arena=None):
    """Choose/prepare, launch, wait for closure, review, and confirm write-back."""
    with stopped(settings["source_world"]):
        registry = discover(archive_files(settings["source_world"]))
    arena = arena or choose_arena(registry)
    if arena is None:
        print("Cancelled; no source changes.")
        return 0
    if arena not in registry:
        raise ValueError(f"Unknown arena {arena!r}; run make edit to choose from the list")
    target = settings["game_dir"] / "saves" / ("Backstabbed-Editor-" + arena)
    # Validate the command before creating a save or doing extraction work.
    launch_invocation(settings, target)
    if not target.exists():
        prepare(settings, arena)
    world = session(settings, arena)
    manifest_path = world / ".backstabbed-editor.json"
    manifest = json.loads(manifest_path.read_text())
    if Path(manifest["source_world"]).resolve() != settings["source_world"].resolve():
        raise ValueError("This editor session belongs to a different source_world; use another instance or move the session aside")
    with stopped(settings["source_world"]):
        check_baseline(settings["source_world"], manifest)
    code = launch_for_edit(settings, arena)
    if code is None:
        return 0
    if code:
        print(f"Launch exited with status {code}; session retained without applying changes.")
        return code
    # Retain both locks throughout review/confirmation/apply. Nested helpers
    # reuse the locks, so Minecraft cannot reopen either save during write-back.
    with stopped(world), stopped(settings["source_world"]):
        check_baseline(settings["source_world"], manifest)
        exported = export(settings, arena)
        record = json.loads((exported / "arena.json").read_text())
        edited = record["state"]
        before = json.loads((world / ".backstabbed-editor-seed.json").read_text())
        old = {o["id"]: o for o in before["objects"]}
        new = {o["id"]: o for o in edited["objects"]}
        print(f"\nReady to write back {arena} to {settings['source_world']}")
        print(f"Objects: {len(new.keys() - old.keys())} added, {len(old.keys() - new.keys())} removed, "
              f"{sum(old[i] != new[i] for i in old.keys() & new.keys())} changed.")
        print(f"Replacement footprint: X/Z {manifest['bounds']} (whole chunks; blocks, decorations, spawns and editor constraints).")
        print(f"Review export: {exported}\nA full verified source backup will be created before writing.")
        try:
            confirmed = input(f"Write this edited arena back to the source world? [Y/n] ").strip().casefold() in ("", "y", "yes")
        except EOFError:
            confirmed = False
        if not confirmed:
            print(f"Source unchanged. Your editor session and export are kept: {exported}")
            return 0
        apply_export(exported, blocks=True)
        # Rebase this persistent session after its own successful write-back so
        # the next make edit resumes it without a false source-conflict error.
        manifest["source_hashes"] = source_hashes(settings["source_world"], manifest["bounds"])
        manifest["last_applied"] = stamp()
        pack.build(world / "datapacks/backstabbed-editor", edited)
        dump(manifest_path, manifest)
        dump(world / ".backstabbed-editor-seed.json", edited)
        print(f"Session updated; make edit {arena} will resume it next time.")
    return 0


def location(item):
    return {"condition": "minecraft:entity_properties", "entity": "this", "predicate": {
        "location": {"dimension": "minecraft:overworld", "position": {
            axis: {"min": item[axis + "1"], "max": item[axis + "2"]} for axis in "xyz"}}}}


def exported_files(state, spec):
    """Portable namespaced functions plus an optional, gated game tick hook."""
    arena = spec["arena"]
    base = f"bbe_arena:{arena}/"
    files = {}

    def function(name, lines):
        files[function_path(base + name)] = ("\n".join(lines) + "\n").encode()

    def predicate(name, value):
        path = f"data/bbe_arena/predicate/{arena}/{name}.json"
        files[path] = (json.dumps(value, indent=2) + "\n").encode()
        return f"bbe_arena:{arena}/{name}"

    spawns = []
    for item in state["objects"]:
        if item["kind"] in ("area", "return"):
            continue
        tags = {"player": ["PlayerSpawn"], "ammo": ["ScrapSpawn"], "both": ["PlayerSpawn", "ScrapSpawn"], "spectator": ["SpectatorSpawn"]}[item["kind"]]
        tags += ["MapEntity", spec["tag"] + "Runtime"]
        value = nbt.Compound({"Tags": nbt.List[nbt.String](tags), "Rotation": nbt.List[nbt.Float]([item["yaw"], item["pitch"]])})
        command = f"summon minecraft:marker {item['x']:.9f} {item['y']:.9f} {item['z']:.9f} {value.snbt()}"
        spawns.append(f"execute {item['guard']} run {command}" if item.get("guard") else command)
    function("spawns", spawns)
    target = next(o for o in state["objects"] if o["kind"] == "return")
    function("tp", [f"execute in minecraft:overworld run tp @s {target['x']:g} {target['y']:g} {target['z']:g} {target['yaw']:g} {target['pitch']:g}"])
    function("kill", ["execute if score $gamestate CmdData matches 1 run return run function mcm:game/playerdeath",
                      f"function {base}tp"])
    areas = [o for o in state["objects"] if o["kind"] == "area" and o["enabled"]]
    keep_in = [location(o) for o in areas if o["mode"] == "keep_in"]
    allowed = {"condition": "minecraft:any_of", "terms": keep_in} if keep_in else {"condition": "minecraft:all_of", "terms": []}
    for item in areas:
        if item["mode"] == "keep_out":
            allowed = {"condition": "minecraft:all_of", "terms": [allowed, {"condition": "minecraft:inverted", "term": location(item)}]}
    predicate("arena", allowed)
    checks = []
    if state["boundary_enabled"]:
        for item in areas:
            if item["mode"] == "keep_out":
                ref = predicate("box_" + str(item["id"]), location(item))
                checks.append(f"execute if predicate {ref} run return run function {base}{item['action']}")
        if keep_in:
            ref = predicate("keep_in", {"condition": "minecraft:any_of", "terms": keep_in})
            checks.append(f"execute unless predicate {ref} run function {base}{state['outside_action']}")
    function("check_player", checks)
    if spec.get("map_id"):
        function("tick", [f"execute unless score $selectedMap CmdData matches {spec['map_id']} run return 0",
                          "execute unless score $gamestate CmdData matches 0..1 run return 0",
                          f"execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. run function {base}check_player"])
    files["pack.mcmeta"] = (json.dumps({"pack": {"pack_format": 61, "description": f"Edited {arena} arena definitions"}}) + "\n").encode()
    return files


def export(settings, arena, output=None):
    world = session(settings, arena)
    target = (output or ROOT / "dev/arena-editor/exports" / (arena + "-" + stamp())).resolve()
    if target.exists():
        raise ValueError(f"Export destination already exists: {target}")
    with stopped(world):
        manifest = json.loads((world / ".backstabbed-editor.json").read_text())
        state = validate(saved_state(world))
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".bbe-export-", dir=target.parent) as temporary:
            staging = Path(temporary) / "export"
            staging.mkdir()
            dump(staging / "arena.json", {"manifest": manifest, "state": state})
            for name, contents in exported_files(state, manifest["spec"]).items():
                path = staging / "datapack" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(contents)
            copy_chunks(world, staging / "world", manifest["bounds"])
            (staging / "README.txt").write_text(
                "Review arena.json and datapack/. The world/ directory contains edited chunks.\n"
                "Apply metadata with: uv run arena-editor/editor.py apply EXPORT_DIRECTORY\n"
                "Add --blocks only to also replace this arena's extracted chunks and decorations.\n"
                "Apply checks the original source hashes and creates a full, verified backup first.\n"
                "The datapack contains callable definitions; use apply to wire them into the game.\n")
            staging.rename(target)
    print(f"Exported {target}\nReview arena.json and datapack/ before applying.")
    return target


def patched_archive(files, state, spec):
    activation = function_path(spec["activation"])
    text = files[activation].decode()
    lines = text.splitlines()
    old_spawns = [line for line in lines if point_from_line(line)]
    hook = f"function bbe_arena:{spec['arena']}/spawns"
    if not old_spawns and hook not in lines:
        raise ValueError("Cannot locate original spawn commands; refusing a partial apply")
    result = dict(files)
    generated = exported_files(state, spec)
    result.update({k: v for k, v in generated.items() if k != "pack.mcmeta"})
    result[f"data/bbe_arena/editor/{spec['arena']}.json"] = (json.dumps(state, indent=2) + "\n").encode()
    result[activation] = ("\n".join(line for line in lines if not point_from_line(line) and line != hook) + "\n" + hook + "\n").encode()
    # Remove only the replaced arena-predicate response commands. Fluid checks,
    # death planes, jump pads and every unrelated map mechanic remain intact.
    namespace = spec["arena"]
    old_boundary = re.compile(rf"\b(?:if|unless) predicate {re.escape(namespace)}:arena\b.*\brun (?:return run )?function (?:mcm:game/playerdeath|{re.escape(namespace)}:(?:escape|return_player|return_to_arena))\s*$")
    prefix = "data/" + spec["activation"].split(":")[0] + "/function/"
    if spec["activation"].startswith("mcm:"):
        prefix += spec["activation"].split(":")[1].removesuffix("activate")
    for name, contents in list(result.items()):
        if name.startswith(prefix) and name.endswith(".mcfunction"):
            result[name] = ("\n".join(line for line in contents.decode().splitlines() if not old_boundary.search(line)) + "\n").encode()
    if not spec.get("map_id"):
        raise ValueError("Cannot safely gate boundary behavior without this arena's map ID")
    tag = "data/minecraft/tags/function/tick.json"
    tick = json.loads(result.get(tag, b'{"values":[]}'))
    ref = f"bbe_arena:{namespace}/tick"
    if ref not in tick["values"]:
        tick["values"].append(ref)
    result[tag] = (json.dumps(tick, indent=2) + "\n").encode()
    # Existing mechanics may refer to this predicate (for example jump pads).
    predicate_name = f"data/{namespace}/predicate/arena.json"
    if predicate_name in result:
        result[predicate_name] = generated[f"data/bbe_arena/predicate/{namespace}/arena.json"]
    return result


def apply_export(directory, *, blocks=False):
    directory = directory.resolve()
    record = json.loads((directory / "arena.json").read_text())
    manifest, state = record["manifest"], validate(record["state"])
    source = Path(manifest["source_world"])
    with stopped(source):
        check_baseline(source, manifest)
        files = patched_archive(archive_files(source), state, manifest["spec"])
        work = ROOT / "dev/arena-editor"
        work.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="apply-", dir=work) as temporary:
            staging = Path(temporary)
            pending = staging / "datapacks/mcm.zip"
            pending.parent.mkdir()
            with zipfile.ZipFile(pending, "w", zipfile.ZIP_DEFLATED) as handle:
                for name, contents in files.items():
                    handle.writestr(name, contents)
            affected = ["datapacks/mcm.zip"]
            if blocks:
                for folder in ("region", "entities", "poi"):
                    for name in footprint(manifest["bounds"]):
                        relative = f"{folder}/{name}"
                        affected.append(relative)
                        if (source / relative).exists():
                            (staging / folder).mkdir(exist_ok=True)
                            shutil.copyfile(source / relative, staging / relative)
                copy_chunks(directory / "world", staging, manifest["bounds"], merge=True)
            backup = work / "backups" / (manifest["spec"]["arena"] + "-" + stamp() + ".zip")
            backup.parent.mkdir(exist_ok=True)
            originals = {p.relative_to(source).as_posix(): digest(p) for p in source.rglob("*") if p.is_file() and p.name != "session.lock"}
            with zipfile.ZipFile(backup, "w", zipfile.ZIP_DEFLATED) as handle:
                for name in originals:
                    handle.write(source / name, name)
            with zipfile.ZipFile(backup) as handle:
                if handle.testzip() or any(hashlib.sha256(handle.read(name)).hexdigest() != sha for name, sha in originals.items()):
                    raise ValueError("Backup verification failed; source is unchanged")
            dump(backup.with_suffix(".json"), {"source_world": str(source), "sha256": digest(backup), "files": originals})
            try:
                for name in affected:
                    destination = source / name
                    if (staging / name).exists():
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        (staging / name).replace(destination)
                    elif destination.exists():
                        destination.unlink()
            except BaseException:
                with zipfile.ZipFile(backup) as handle:
                    for name in affected:
                        destination = source / name
                        if name in originals:
                            destination.parent.mkdir(parents=True, exist_ok=True)
                            destination.write_bytes(handle.read(name))
                        elif destination.exists():
                            destination.unlink()
                raise
    print(f"Applied {manifest['spec']['arena']} {'metadata and chunks' if blocks else 'metadata'} to {source}\nVerified backup: {backup}")
    print(f"Reviewed export retained at {directory}.")
    return backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(os.environ.get("BBE_EDIT_CONFIG") or HERE / "config.local.json"))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List arenas discovered from the voting table")
    edit_parser = sub.add_parser("edit", help="Choose/launch an arena, then confirm writing it back after closure")
    edit_parser.add_argument("arena", nargs="?", default=os.environ.get("BBE_EDIT_ARENA") or None)
    init = sub.add_parser("init-config", help="Create the ignored local configuration")
    prepare_parser = sub.add_parser("prepare", help="Extract one arena into a persistent creative void world")
    prepare_parser.add_argument("arena")
    prepare_parser.add_argument("--bounds", type=int, nargs=4, metavar=("MIN_X", "MIN_Z", "MAX_X", "MAX_Z"))
    launch_parser = sub.add_parser("launch", help="Run the locally configured instance launch command")
    launch_parser.add_argument("arena")
    export_parser = sub.add_parser("export", help="Export saved metadata and edited chunks for review")
    export_parser.add_argument("arena")
    export_parser.add_argument("--output", type=Path)
    apply_parser = sub.add_parser("apply", help="Back up and apply a reviewed export to its original source")
    apply_parser.add_argument("directory", type=Path)
    apply_parser.add_argument("--blocks", action="store_true", help="Also replace the extracted chunks and decorations")
    args = parser.parse_args()
    try:
        if args.command == "init-config":
            if args.config.exists():
                raise ValueError(f"Config already exists: {args.config}")
            args.config.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / "config.example.json", args.config)
            print(f"Edit {args.config} to set your instance and launch command.")
            return 0
        if args.command == "apply":
            apply_export(args.directory, blocks=args.blocks)
            return 0
        settings = config(args.config)
        if args.command == "edit":
            return edit(settings, args.arena)
        elif args.command == "list":
            with stopped(settings["source_world"]):
                registry = discover(archive_files(settings["source_world"]))
            for name, spec in sorted(registry.items(), key=lambda pair: pair[1].get("map_id") or 999):
                print(f"{name:20} map {str(spec['map_id']):>2}  bounds {spec.get('bounds', 'requires --bounds')}")
        elif args.command == "prepare":
            prepare(settings, args.arena, args.bounds)
        elif args.command == "launch":
            return launch(settings, args.arena)
        elif args.command == "export":
            export(settings, args.arena, args.output)
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(1, f"Error: {error}\n")
    except KeyboardInterrupt:
        parser.exit(130, "\nCancelled. The editor session and completed exports are kept.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
