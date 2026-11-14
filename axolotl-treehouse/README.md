# Axolotl Treehouse / 水帘树洞

Arena **25** imports the original **siyuan_水帘树洞.litematic** supplied by the user,
from [siyuan_日记's showcase](https://www.bilibili.com/video/BV1fDNJ6qEpx).
The [tutorial's pinned comment](https://www.bilibili.com/video/BV1GrKw6yEFM)
provides the [original download](https://pan.baidu.com/s/19aUMmSI5S1PpEcLJgvz_Nw?pwd=v8ch).
The schematic metadata credits `bi_bi_233`; both attributions are retained.
No explicit reuse license accompanied the file; this records provenance without
asserting a broader permission grant.

The original **7,745 blocks and all their block states** remain at translated
coordinates. The source is 34 × 36 × 37 blocks, with DataVersion 4671, and is
placed at **[57583, 73, 57582]**, without rotation. All 11 source entities and
73 ordinary block entities are retained. The 98 empty shelf block entities are
omitted because the visual shelf block has no inventory. Entity coordinates
and attachments are translated, UUIDs are regenerated, and decorative animals
are persistent and invulnerable. No source command blocks or datapacks are imported.

The surrounding island is a heuristic reconstruction guided by the user's video
screenshot: broken stone cliffs, a walk-through arch and raised bluff, winding
paths, a small quay with descending stairs, a timber pavilion, wheat patches,
crooked trees, swings, flowers and mossy retaining walls. The six smaller trees
sample 501 branch/foliage blocks from the original central tree, scaled and
rotated around the island. This preserves its azalea leaves, oak bark, wooden
twigs and hanging vines. The original house is overlaid separately; the terrain
generator never recreates it.

The lake and mountain basin measures **512 × 512 blocks**, centered at
**[57600, 57600]**, in new region `r.112.112.mca`. The surrounding mountains are
an actual **1,024-chunk Minecraft Java 1.21.4 overworld sample**, seed
`69420018030897796`, source center `[128, 0]`. Native terrain, trees and rock
remain outside a 34-block shoreline transition. A native ridge from the same
sample closes the low southern valley mouth, with a 20-block transition at its
edges; its donor and destination bounds are recorded in the manifest. The widened lake follows the
connected low valley, with a guaranteed 128-block open central radius before
the island is inserted. This replaces the earlier synthetic mountain recipe.
`build/prepare_vanilla.py` records the transform and native surface samples;
the regression check compares those samples against the installed world.
Native trees are extracted before grading and restored with one vertical
translation per complete trunk/branch/canopy group. Trees whose roots would be
in the lake are omitted. Six complete moved trees are also checked block for
block to prevent stretched canopies from returning.

Use `/function axolotl_treehouse:select` while no round is active, or vote for
the **Axolotl Treehouse** poster. There are 32 distinct player/scrap markers,
distributed across the landscape and the original house, and one spectator
marker above the island. Source architecture, terrain and all spawn candidates
are checked against the actual saved blocks; the native test also checks the
player collision volume, support and at least two onward routes per spawn.

From round start, **including grace**, a live queued player whose feet reach
Y64 or lower outside the exact island/dock footprint is eliminated through
`mcm:game/playerdeath`. No fluid-contact predicate is used. The source ponds,
water curtain, waterlogged decorations and incidental water contact remain
harmless. A waiting player is returned safely instead. The hard limits are
X/Z57536–57663.999999, Y63–150 in the overworld; horizontal/vertical escapes
return during grace and eliminate afterward. Mountains are outside those limits
and separated by roughly 70 or more blocks of open water. Spectators, dead
players, nonparticipants and other maps are excluded.

`backstabbed-treehouse-1.0.0.jar` is **required on both client and server**.
It registers visual-only `minecraft:spruce_shelf`, `minecraft:firefly_bush` and
`minecraft:cactus_flower` blocks using the original IDs. Shelves retain facing,
waterlogging, powered and side-chain state properties and the matching shallow
collision geometry. Shelf inventory/redstone exchange and new plant gameplay
are intentionally absent, as requested. The assets come from the official
Minecraft 1.21.9 client; the small copied asset set and hashes are recorded in
[assets-provenance.json](assets-provenance.json). Plant models add NeoForge's
cutout render type. The mod does not register custom networking or change worldgen.

Existing options were researched before adding this mod.
[Shelf Backport](https://modrinth.com/mod/shelfs) lists 1.21.4 but implements the
full shelf feature set; [Copper Age Backport](https://modrinth.com/mod/backport-copper-age/versions)
and [content-backport](https://modrinth.com/mod/content-backport) target other
Minecraft versions. The three-block visual mod keeps this port's dependency and
behavior changes limited to the appearance requested by the user.

The poster is generated with OpenAI built-in imagegen. Its exact prompt is in
[poster-prompt.txt](poster-prompt.txt). The installed texture, item model, atlas
entry and voting display use `axolotl_treehouse:posters/axolotl_treehouse` and
the existing Z8 / X−0.01 booth convention.

The full manifest is [docs/arenas/axolotl_treehouse.json](../docs/arenas/axolotl_treehouse.json).
Original downloads, converted structures and previews remain in the Git-ignored
`map-previewer/maps/axolotl-treehouse/` directory. The island preview is served
at `http://127.0.0.1:5222/` while the preview process is running. Preview rendering
does not replace native collision and gameplay tests.

Rebuild the mod with `python axolotl-treehouse/build_mod.py`. The generation and
import tools are under `build/`; they use the installed minecraft-builder skill
runner and `uv run --no-project --with nbtlib --with numpy`; preparing the native
shoreline additionally needs `--with scipy`. Import refuses an occupied region
unless `--replace-own-scene` is supplied, and even then verifies that it contains
exactly this scene's chunk slots. `--preview-only` prepares the proposed island
without writing world regions. `build/install_datapack.py` installs the maintained
namespace and shared hooks while preserving unrelated ZIP entries.

Run the focused static checks with:

```sh
uv run --no-project --with nbtlib python -m unittest discover -s tests -p test_axolotl_treehouse.py -v
```

Run the disposable target-version client/server test with:

```sh
make resourcepack
xvfb-run -a -s '-screen 0 1600x1000x24' uv run --no-project --with portablemc==4.4.1 python axolotl-treehouse/tests/run.py
```

The test uses four participants, normal voting and role assignment, native
collision queries, lake/pond/perimeter probes, reload, reset and screenshots.
It copies the world into a disposable game directory; it never runs Minecraft
against the source save.

The [verification record](../docs/arenas/axolotl_treehouse-verification.json)
contains the final screenshot paths, package hashes and backup information.
All eight focused checks pass. The four-player native gameplay run passed 133
assertions; a separate final visual run checked the corrected distant forest.
The full 72-test suite retains the pre-existing two Monolith failures and one
Linux `msvcrt` import error in the Meridian boundary-policy checks. Compared
with the initial backup, 971 prior world files are unchanged, the shared
datapack is updated, and only this arena's region/entity files are added.

The verified full-save backup before importing is
`.minecraft/backups/map-integration/20261109T150803338789Z-axolotl-treehouse-before-import-71435139.zip`,
SHA-256 `672245cbfd57c5977c2834e2c3a557c61c66d5b8e2f6af42fb17e03f36a3c82c`.
The verified full-save backup before the authorized landscape redesign is
`.minecraft/backups/map-integration/20261109T160006889268Z-treehouse-before-island-redesign-034646ff.zip`,
SHA-256 `747b57db40c89644780a5b82b45f18963022c9d6852be20230da53832b041f58`.
The verified full-save backup before replacing the mountains and rebuilding the
reference trees is
`.minecraft/backups/map-integration/20261109T161916700927Z-treehouse-before-vanilla-terrain-rebuild-6cbc708a.zip`,
SHA-256 `f89345069a75232308cdc095fe3a7927eda0f8c91b9267a44cfdda4fb0562376`.
To restore, stop Minecraft, verify the archive with the project skill's
`backup_world.py --verify`, move the current save aside, and extract the archived
world folder under `.minecraft/saves/`. Preserve all backup archives.
