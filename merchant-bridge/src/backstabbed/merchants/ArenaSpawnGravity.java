package backstabbed.merchants;

import com.mojang.brigadier.exceptions.SimpleCommandExceptionType;
import gravity_changer.api.GravityChangerAPI;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.Marker;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.event.RegisterCommandsEvent;

/** Apply a spawn marker's gravity synchronously, before the datapack teleports.
 * The Gravity Changer marker bridge deliberately supports non-player targets.
 */
public final class ArenaSpawnGravity {
    private static final SimpleCommandExceptionType INVALID = new SimpleCommandExceptionType(
        Component.literal("Expected a same-dimension spawn marker with a valid gravity direction and positive finite strength"));

    private ArenaSpawnGravity() {}

    public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("arena_spawn_gravity")
            .requires(source -> source.hasPermission(2))
            .then(Commands.argument("marker", EntityArgument.entity()).executes(context -> {
                var player = context.getSource().getPlayerOrException();
                var entity = EntityArgument.getEntity(context, "marker");
                if (!(entity instanceof Marker marker) || entity.level() != player.level())
                    throw INVALID.create();
                var data = marker.saveWithoutId(new CompoundTag()).getCompound("data");
                Direction direction = data.contains("gravity_direction")
                    ? Direction.byName(data.getString("gravity_direction")) : Direction.DOWN;
                double strength = data.contains("gravity_strength") ? data.getDouble("gravity_strength") : 1.0;
                if (direction == null || !Double.isFinite(strength) || strength <= 0)
                    throw INVALID.create();
                player.stopRiding();
                GravityChangerAPI.setBaseGravityDirection(player, direction);
                GravityChangerAPI.setBaseGravityStrength(player, strength);
                var gravity = GravityChangerAPI.getGravityComponent(player);
                gravity.updateGravityStatus(false);
                gravity.applyGravityChange();
                player.setDeltaMovement(Vec3.ZERO);
                player.fallDistance = 0;
                return 1;
            })));
    }
}
