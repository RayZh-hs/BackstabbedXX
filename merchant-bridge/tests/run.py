"""Run merchant regression checks and real client menu checks in a disposable 1.21.4 world.

Run with uv run --no-project --with portablemc==4.4.1 python merchant-bridge/tests/run.py.
Set DISPLAY to an Xvfb display if the user's game is already open.
"""
from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import subprocess
import sys
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "scripts"))
import launch
import local_playtest

runtime = root / "dev/launcher"
output = root / "dev/merchants"
output.mkdir(exist_ok=True)
(output / "results.txt").unlink(missing_ok=True)
library = runtime / "libraries/net/neoforged/neoforge/21.4.158"
priority = [library / f"neoforge-21.4.158-{kind}.jar" for kind in ("client", "universal")]
jars = priority + sorted(p for p in (runtime / "libraries").rglob("*.jar") if p not in priority)
classes = output / "test-classes"
classes.mkdir(exist_ok=True)
subprocess.run([str(runtime / "jvm/java-runtime-delta/bin/javac"), "--release", "21", "-proc:none",
                "-classpath", os.pathsep.join(map(str, jars)), "-d", str(classes),
                str(root / "merchant-bridge/tests/MerchantRegression.java")], check=True)
jar = output / "merchant-tests.jar"
with ZipFile(jar, "w", compression=ZIP_DEFLATED) as z:
    z.writestr("META-INF/neoforge.mods.toml", '''modLoader="javafml"
loaderVersion="[4,)"
license="All Rights Reserved"
[[mods]]
modId="backstabbed_merchant_test"
version="1.0.0"
displayName="Disposable Merchant Regression"
''')
    for p in classes.rglob("*.class"):
        z.write(p, p.relative_to(classes).as_posix())

original = local_playtest.local_game_directory
@contextmanager
def directory(root):
    with original(root) as game:
        shutil.copyfile(jar, game / "mods/merchant-tests.jar")
        p = game / "saves" / local_playtest.WORLD_NAME / "datapacks/mcm.zip"
        with ZipFile(p) as z:
            entries = {name:z.read(name) for name in z.namelist()}
        # Exercise the actual map functions explicitly while suppressing unrelated
        # round timers and lobby teleports in this isolated regression fixture.
        entries["data/minecraft/tags/function/tick.json"] = b'{"values":[]}'
        with ZipFile(p, "w", compression=ZIP_DEFLATED) as z:
            for name,data in entries.items(): z.writestr(name,data)
        try:
            yield game
        finally:
            if (game / "logs").exists():
                shutil.copytree(game / "logs", output / "logs", dirs_exist_ok=True)
            if (game / "screenshots").exists():
                shutil.copytree(game / "screenshots", output / "screenshots", dirs_exist_ok=True)
local_playtest.local_game_directory = directory
# The actual connected client is sufficient for this fixture; idle clients do
# not negotiate Gravity Changer's login payloads in the current helper.
local_playtest.build_helper = lambda *args, **kwargs: None
os.environ["BACKSTABBED_MERCHANT_TEST_OUTPUT"] = str(output / "results.txt")
sys.argv = ["launch.py", "--local", "--resolution", "1280x800"]
try:
    launch.main()
except SystemExit as exit:
    if exit.code not in (None, 0):
        raise
result = output / "results.txt"
if not result.exists() or not result.read_text().startswith("PASS\n"):
    raise SystemExit(result.read_text() if result.exists() else "Merchant checks did not finish; inspect dev/merchants/logs.")
print(result.read_text())
