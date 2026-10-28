# KLUT-27 large-fire rebuild

Use current standalone scene as canonical; 45 differences include 35 new fuel blocks and five removed glass blocks. Preserve all unrelated saves, mod .3 and existing roles. Back up three saves and preview authorized elevator replacement first.

1. Synchronize current scene changes and insert a locked Simple Elevators block at (8,15,20), keeping two headroom blocks.
2. Rebuild connected fuel graph from the pristine new scene. Retain 60 ticks per block and exact decorative-support cleanup, expand restoration to every affected block/entity.
3. Detect contact with a burning block in each elevator's 26-neighbour shell, never a radius-3 approximation. Each elevator explodes once. Destroy radius-2 fuel, ignite surviving adjacent fuel, kill radius-3 villagers and live players, exclude all golems. Restore killed original villagers next round.
4. Dispatch only burning cells via function macros, avoiding per-tick scans for hundreds of individual cells; persist jobs across reload and migrate old fire state safely.
5. Test face/edge/corner contact and two-block gap, real new elevator transfer, villager death/golem immunity, timing and full scene restoration. Run repository and both actual server suites, verify byte-identical integrated packs.
