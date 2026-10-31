"""Check all six Cube Block spawn orientations and a normal four-player round.

Run with uv run --no-project --with portablemc==4.4.1 python merchant-bridge/tests/run_cube.py.
Uses a disposable world; results are retained under dev/cube-face-check/.
"""
from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'scripts'))
import launch
import local_playtest

work = root / 'dev/cube-face-check'
work.mkdir(parents=True, exist_ok=True)
(work / 'results.txt').unlink(missing_ok=True)
runtime = root / 'dev/launcher'
compiler = runtime / 'jvm/java-runtime-delta/bin/javac'
library = runtime / 'libraries/net/neoforged/neoforge/21.4.158'
priority = [library / 'neoforge-21.4.158-client.jar', library / 'neoforge-21.4.158-universal.jar']
jars = priority + sorted(p for p in (runtime / 'libraries').rglob('*.jar') if p not in priority)
jars += list((root / '.minecraft/mods').glob('*.jar'))
classes = work / 'classes'
classes.mkdir(exist_ok=True)
subprocess.run([str(compiler), '--release', '21', '-proc:none', '-classpath', os.pathsep.join(map(str, jars)),
                '-d', str(classes), str(root / 'merchant-bridge/tests/FaceChecks.java')], check=True)
jar = work / 'port-checks.jar'
with zipfile.ZipFile(jar, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr('META-INF/neoforge.mods.toml', '''modLoader="javafml"
loaderVersion="[4,)"
license="All Rights Reserved"
[[mods]]
modId="backstabbed_regression"
version="1.0.0"
displayName="Disposable Arena Port Checks"
''')
    for p in classes.rglob('*.class'):
        z.write(p, p.relative_to(classes).as_posix())
original = local_playtest.local_game_directory
@contextmanager
def checked_directory(root):
    with original(root) as game:
        shutil.copyfile(jar, game / 'mods/backstabbed-port-checks.jar')
        options = game / 'options.txt'
        values = options.read_text().splitlines() if options.exists() else []
        overrides = {'pauseOnLostFocus': 'false', 'maxFps': '60', 'renderDistance': '8', 'simulationDistance': '6'}
        values = [line for line in values if line.partition(':')[0] not in overrides]
        options.write_text('\n'.join(values + [key + ':' + value for key, value in overrides.items()]) + '\n')
        try:
            yield game
        finally:
            for name in ('logs', 'crash-reports'):
                if (game / name).exists(): shutil.copytree(game / name, work / name, dirs_exist_ok=True)
local_playtest.local_game_directory = checked_directory
os.environ['ARENA_CHECK_DIR'] = str(work)
sys.argv = ['launch.py', '--local', '--resolution', '1100x760']
launch.main()

result = work / 'results.txt'
if not result.exists() or not result.read_text().startswith('PASS\n'):
    raise SystemExit(result.read_text() if result.exists() else 'Cube checks did not finish; inspect dev/cube-face-check/logs.')
print(result.read_text())
