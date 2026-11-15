# Bullet visual alignment — datapack/resource-only repair

The map uses the existing GravityChanger .3 binary and production source unchanged.
Projectile speed, muzzle, ownership, ammunition, recoil, lifetime and damage rules
are preserved.

## Two independent client/server problems

The original resource correction centered the model at pixel (8, 8, 8), preserving
size, faces, UVs and textures. Correct server-side geometry alone was insufficient.

In Minecraft 1.21.4, both `ClientboundAddEntityPacket` and
`ClientboundSetEntityMotionPacket` clamp each velocity component to +/-3.9.
The gun fires at speed 7. At yaw 31 degrees and pitch 0, the server velocity is
approximately (-3.60505, 0, 6.00030); the client receives (-3.605, 0, 3.9).
This bends the client-predicted direction by 11.751 degrees. A display riding that
arrow follows the incorrect client trajectory. Normal downward gravity and lobby
shots are also affected.

An immediate dismount was not sufficient. Vanilla `ServerEntity.sendPairingData`
sends the initial passenger list, but does not update `lastPassengers`, which starts
empty. If the passenger is removed before the first `sendChanges`, the current list
is also empty. No empty passenger packet is sent. The server has dismounted the
display, but the client still considers it a passenger for the entire bullet lifetime.
A real packet-sequence regression reproduces this: `serverPassenger=false`, while
the client's last received passenger list still contains the display entity ID.
This is a vanilla tracking-state synchronization defect, not a resource-pack offset.

## Correct generation and update sequence

1. `try_fire` summons the arrow with an **empty, invisible** `BulletTemplate`
   item display passenger. The original gravity bridge computes its rotation and
   transformation as before, and initializes the real arrow's physics.
2. `setspeed` stores the arrow's full UUID. `align_visual` copies the template's
   initialized rotation and transformation, with zero translation.
3. `spawn_visual` summons a **new independent** visible `BulletDeco` at that arrow's
   true muzzle position. Its first spawn already has the final pose and model.
   This visible entity is never a passenger. The empty template is killed immediately.
   Its entity ID is never reused for the visible bullet.
4. At the end of `game/items/gun/shoot`, every visible display invokes `sync_visual`
   with its stored arrow UUID. It follows that exact arrow or removes itself when
   the arrow is gone. Nearest-display cleanup is removed; crossing/coincident shots
   cannot remove another shot's display. Range expiry removes the corresponding
   visual in the same function tick. Legacy displays without a UUID are cleaned up.

Item displays transmit positions every tick. `teleport_duration:1` interpolates
between authoritative positions without using clamped arrow velocity prediction.
Transformation interpolation is disabled. Normal tick/network interpolation latency
remains; it does not bend the visible path sideways. Relative summon coordinates
preserve the exact muzzle, including integer X/Z positions without block centering.

## Maintained files and verification

`bullet-visual/datapack/` contains the helpers. `scripts/bullet_visual.py` is an
idempotent overlay limited to `extensions/gun/try_fire`, `extensions/gun/setspeed`,
`game/items/gun/shoot`, and the visual helpers. The obsolete
`capture_visual_offset` helper is removed. The canonical map archive contains the
complete overlay. No terrain, player data or mod binary changes are needed.

`bullet-visual/tests/BulletVisualDatapackTests.java` uses the existing NeoForge
GameTest harness and original mod production code. Tests reproduce the real vanilla
velocity clamp and pairing/dismount packets. They invoke the **actual try_fire
function** and observe entity creation through `EntityJoinLevelEvent`, verifying
that no visible bullet ever spawns mounted and that its initial position/rotation
are final before tracking starts. Earlier tests that constructed a tracker only
after dismount missed the initial passenger packets.

Position tests cover 6 gravity directions, 8 yaw angles and 3 pitches (144 combinations),
actual `ServerEntity` position-packet endpoints and interpolated segments. Tests also
check original arrow physics/orientation, caller-position independence, coincident
shot UUID isolation, missing-arrow cleanup and range-expiry cleanup. Python tests
check resource geometry, archive/source agreement and migration scope/idempotence.
These automated checks are distinct from a live client-screen visual test.

To install into Prism, close Minecraft and use the maintained sync script with
`-GameplayOnly` and the intended checkout as `-ProjectPath`. It backs up and updates
the datapack/resource pack while retaining mods, terrain and player data.
