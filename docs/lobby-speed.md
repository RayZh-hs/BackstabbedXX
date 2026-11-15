# Lobby Speed II

Players physically inside the existing overworld lobby bounds continuously receive
Speed II (amplifier 1), refreshed for one second with particles hidden. This also
applies to queued players and players remaining in the lobby while others play.

Outside the lobby the effect is not refreshed and expires within 20 ticks. No
blanket speed clearing is performed, so arena speed bonuses are preserved.
Vanilla effect priority preserves stronger test-range adrenaline effects.

`lobby-speed/datapack/data/mcm/function/lobby/speed.mcfunction` contains the
maintained function; `scripts/lobby_speed.py` installs it and appends its call to
the existing lobby function. `lobby-speed/tests/LobbySpeedTests.java` checks lobby
and arena scope, other dimensions, effect level/duration, stronger-effect priority
and expiry after leaving.
