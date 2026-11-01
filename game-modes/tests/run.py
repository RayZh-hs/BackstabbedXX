"""Run real Minecraft command regression checks in a disposable client world.

uv run --no-project --with portablemc==4.4.1 python game-modes/tests/run.py
"""
from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import subprocess
import sys
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'scripts'))
import launch
import local_playtest

runtime = root / 'dev/launcher'
output = root / 'dev/game-modes'
output.mkdir(parents=True, exist_ok=True)
(output / 'results.txt').unlink(missing_ok=True)
library = runtime / 'libraries/net/neoforged/neoforge/21.4.158'
priority = [library / f'neoforge-21.4.158-{kind}.jar' for kind in ('client', 'universal')]
jars = priority + sorted(p for p in (runtime / 'libraries').rglob('*.jar') if p not in priority)
classes = output / 'classes'
classes.mkdir(exist_ok=True)
subprocess.run([str(runtime / 'jvm/java-runtime-delta/bin/javac'), '--release', '21', '-proc:none',
                '-classpath', os.pathsep.join(map(str, jars)), '-d', str(classes),
                str(root / 'game-modes/tests/ModeRegression.java')], check=True)
jar = output / 'mode-tests.jar'
with ZipFile(jar, 'w', compression=ZIP_DEFLATED) as z:
    z.writestr('META-INF/neoforge.mods.toml', '''modLoader="javafml"
loaderVersion="[4,)"
license="All Rights Reserved"
[[mods]]
modId="backstabbed_mode_test"
version="1.0.0"
displayName="Disposable Mode Regression"
''')
    for p in classes.rglob('*.class'):
        z.write(p, p.relative_to(classes).as_posix())

original = local_playtest.local_game_directory
@contextmanager
def directory(root):
    with original(root) as game:
        shutil.copyfile(jar, game / 'mods/mode-tests.jar')
        p = game / 'saves' / local_playtest.WORLD_NAME / 'datapacks/mcm.zip'
        with ZipFile(p) as z:
            entries = {name: z.read(name) for name in z.namelist()}
        entries['data/minecraft/tags/function/tick.json'] = b'{"values":[]}'
        with ZipFile(p, 'w', compression=ZIP_DEFLATED) as z:
            for name, data in entries.items():
                z.writestr(name, data)
        try:
            yield game
        finally:
            if (game / 'logs').exists():
                shutil.copytree(game / 'logs', output / 'logs', dirs_exist_ok=True)
local_playtest.local_game_directory = directory
local_playtest.build_helper = lambda *args, **kwargs: None
os.environ['BACKSTABBED_MODE_TEST_OUTPUT'] = str(output / 'results.txt')
sys.argv = ['launch.py', '--local', '--resolution', '960x540']
try:
    launch.main()
except SystemExit as exit:
    if exit.code not in (None, 0):
        raise
result = output / 'results.txt'
if not result.exists() or not result.read_text().startswith('PASS\n'):
    raise SystemExit(result.read_text() if result.exists() else 'Mode checks did not finish; inspect dev/game-modes/logs.')
print(result.read_text())
