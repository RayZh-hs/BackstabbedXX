# Arena merchants

Right-click the actual NPC to open Minecraft's normal trading screen. Opening
the screen does not purchase anything; payment happens when the result is taken.

| Arena | NPC and location | Offer |
| --- | --- | --- |
| Underwater Base (19) | Zombie diving-suit trader, `32963.5 48.0625 32460.5`, beside the hydroponics counter and cyan locker | 4 scraps → one drinkable 20-second invisibility potion |
| Panda Village (13) | Existing panda toy merchant, `8370.5 106 8373.5` | 4 scraps → the existing non-firing toy gun |

Both shops require a living, queued, non-spectating player within five blocks
in the selected arena during an active round. Menus become invalid when those
conditions change, the NPC disappears, or the map resets. Vanilla merchant slots
handle inventory capacity, payment, repeated purchases and returning unused
inputs. Offers have fixed prices, no XP rewards and effectively unlimited stock.
Each viewer has an independent menu session, allowing simultaneous customers.
The `ArenaMerchants` team disables entity pushing so neither NPC can be moved
away from its shop and offer-data marker by players.

The NPC and its invisible, non-interactive offer-data marker use `MapEntity` and
their arena's runtime tag. Normal activation recreates them, and reset removes
them. The old panda interaction entity and immediate purchase advancement are
retired. Existing toy-gun components, model, lore and non-firing behavior remain
the same.

## Host mod and resource pack

The server-side NeoForge mod is
`.minecraft/mods/backstabbed-merchants-1.0.0.jar`; its complete source is under
`src/`. It opens the vanilla merchant menu when the actual panda or zombie is
clicked. It registers no entity types, menus, mixins, items or network payloads.
The private merchant session is an unspawned villager because vanilla's
shift-click sound code requires the merchant to be an entity. It creates no
hidden villager in the world, additional hitbox or ticking mob.

The host needs this mod on NeoForge 21.4.158 / Minecraft 1.21.4. The standard
client pack includes it, though the bridge has no client networking requirement.
A Fabric arena editor can display copied NPCs and equipment with the resource
pack; trading itself requires the NeoForge host. Arena NPCs are spawned by the
game's activation functions, rather than saved into the map's entity regions.

Minecraft 1.21.4 uses custom equipment assets for the copper suit. The zombie's
boots, leggings and chestplate reference `underwater_base:copper`. Its helmet
item model combines an oxidized copper grate head with the copper helmet shell,
so all four copper armor pieces remain visible. These are NPC-only equipment
overrides and do not replace ordinary iron armor textures.

The two copper armor PNGs are Mojang's original 64×32 textures from Java 1.21.9,
downloaded using Mojang's version manifest and verified against the official
client JAR's SHA-1, `ce92fd8d1b2460c41ceda07ae7b3fe863a80d045`. They are at:

- `assets/underwater_base/textures/entity/equipment/humanoid/copper.png`
- `assets/underwater_base/textures/entity/equipment/humanoid_leggings/copper.png`

The grate uses the game's existing `minecraft:block/oxidized_copper_grate`
texture. Equipment, helmet model, item definition, atlas and translations are in
the resource-pack source under `.minecraft/resourcepacks/backstabbed-resource/`.

## Update and verify

After changing Java source, rebuild against the launcher's installed dependencies:

```sh
python3 merchant-bridge/build.py
```

The shipped JAR includes source checksums; `make test` verifies the checked-in
artifact matches its source. The build requires Java 21 and the pinned libraries
installed by `make launch`, and accepts `--runtime PATH` for another cache.
Ordinary modpack/release builds use the shipped JAR and require only Python.

Reviewable copies of the changed datapack members are in `datapack/`. To apply
changes to those copies, close the source world and run:

```sh
python3 merchant-bridge/sync_datapack.py
make test
make resourcepack
```

The sync script refuses an open source world and preserves all other ZIP
members. It appends only the underwater merchant activation hook, preserving
the arena's existing spawn points, decorations and lifecycle logic.

For runtime checks, use a disposable copy with a real NeoForge client:

```sh
xvfb-run -a -s '-screen 0 1280x800x24' \
  uv run --no-project --with portablemc==4.4.1 \
  python merchant-bridge/tests/run.py
```

The regression fixture explicitly invokes map lifecycle functions while disabling
unrelated automatic round/lobby ticks. It checks both native menus, purchases,
refunds, inventory capacity, potion consumption, access restrictions, menu
invalidation and reset, and sends real client interaction packets to each NPC.
Results, logs and screenshots are saved under ignored `dev/merchants/`.

## Recovery snapshot

Before this integration, the complete source world was backed up and verified:

```text
.minecraft/backups/map-integration/20261028T162646913279Z-merchants-before-change-cccfbacf.zip
SHA256: 7dec43c7622e8f92ee8c249758005c18f13670983b8242a0f3a91feef320723d
```

To restore, close Minecraft, verify the archive using the map integration skill's
`backup_world.py --verify`, move the current save aside, and extract the archived
world folder under `.minecraft/saves/`. Keep the backup. The integration changes
datapack and resource-pack content and adds the host mod; it does not modify map
blocks or saved entity/POI regions.
