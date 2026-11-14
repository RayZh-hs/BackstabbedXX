# Bullet visual alignment — datapack/resource-only repair

This fix uses only the map datapack and resource pack. The existing GravityChanger
.3 binary and its production source remain unchanged.

The resource model now centers its existing geometry at pixel (8, 8, 8). Its old
center was (7, 5.5, 7). Size, faces, UVs and textures are preserved.

Arrow passenger seating adds +0.5 world-Y. After the unchanged .3 bridge initializes
world aim and display rotation, `extensions/gun/setspeed` runs `align_visual` as and
at that bullet display. Vanilla local coordinates calculate the inverse display
rotation of (0, -0.5, 0), stored as display translation. The helper marker is removed
immediately; no persistent entity or scoreboard objective is added. Transform
interpolation is disabled to prevent drifting during the eight-tick bullet lifetime.

Source: `bullet-visual/datapack/` and the idempotent `scripts/bullet_visual.py` overlay.
The overlay changes only `extensions/gun/setspeed` and adds `extensions/gun/align_visual`
and `extensions/gun/capture_visual_offset`. The helper is addressed directly through
execute-summon, so no loaded chunk at world origin is required.
It preserves all projectile velocity, muzzle, owner, ammunition, recoil and damage logic.

Regression source lives in `bullet-visual/tests/BulletVisualDatapackTests.java` and
runs in the existing GameTest harness against the original mod production code.
It exercises the real setspeed function, original display matrix, six gravity
directions and three pitches, checking center across movement, orientation and
immediate alignment. Python tests check actual resource geometry and overlay scope.
Client-screen visual confirmation remains separate from server tests.

To install, close Minecraft and back up the target world's `datapacks/mcm.zip`
and resource pack. Replace that datapack with the project's updated archive and
rebuild the resource pack using `python scripts/build.py resourcepack`. Install
the resulting resource ZIP on clients. No mod, terrain or player-data replacement
is required.

Verification: the restored-mod baseline failed the new regression; the corrected
datapack passed the six-direction / three-pitch check and the 50 registered server
tests (map-specific opt-in cases retain their existing skip rules). Two Python
checks passed. The installed JAR is verified unchanged against Git.
