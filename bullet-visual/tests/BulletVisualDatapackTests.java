package gravity_changer.test;
import gravity_changer.api.GravityBridge;
import gravity_changer.api.GravityChangerAPI;
import net.minecraft.core.Direction;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;
@net.neoforged.fml.common.EventBusSubscriber(modid="gravity_changer", bus=net.neoforged.fml.common.EventBusSubscriber.Bus.MOD)
@PrefixGameTestTemplate(false)
public final class BulletVisualDatapackTests {
    @net.neoforged.bus.api.SubscribeEvent
    public static void register(net.neoforged.neoforge.event.RegisterGameTestsEvent event) { event.register(BulletVisualDatapackTests.class); }
    @GameTest(template = "empty", templateNamespace = "gravity_changer")
    public static void bulletVisualCenterFollowsTrajectory(GameTestHelper h) {
        var shooter = h.spawn(EntityType.PIG, 8, 8, 8);
        for (Direction direction : Direction.values()) {
            GravityChangerAPI.setBaseGravityDirection(shooter, direction);
            GravityChangerAPI.getGravityComponent(shooter).applyGravityChange();
            for (float pitch : new float[]{-75, 0, 43}) {
                shooter.setYRot(31); shooter.setXRot(pitch);
                var arrow = h.spawn(EntityType.ARROW, 3, 3, 3);
                var display = h.spawn(EntityType.ITEM_DISPLAY, 3, 3, 3);
                display.addTag("BulletDeco");
                var displayData = display.saveWithoutId(new CompoundTag());
                var matrix = new net.minecraft.nbt.ListTag();
                for (float value : new float[]{1.6f,0,0,0, 0,0,1.6f,0, 0,1.6f,0,0, 0,0,0,1})
                    matrix.add(net.minecraft.nbt.FloatTag.valueOf(value));
                displayData.put("transformation", matrix);
                displayData.putInt("interpolation_duration", 8);
                display.load(displayData);
                display.startRiding(arrow, true);
                GravityBridge.fire(shooter, arrow);
                h.getLevel().getServer().getCommands().performPrefixedCommand(
                    h.getLevel().getServer().createCommandSourceStack().withEntity(arrow).withLevel(h.getLevel()).withPosition(arrow.position()).withRotation(arrow.getRotationVector()).withPermission(2).withSuppressedOutput(),
                    "function mcm:extensions/gun/setspeed");
                var transform = com.mojang.math.Transformation.CODEC.parse(net.minecraft.nbt.NbtOps.INSTANCE,
                    display.saveWithoutId(new CompoundTag()).get("transformation")).result().orElseThrow();
                var orientation = new org.joml.Quaternionf().rotationYXZ(
                    (float)Math.toRadians(-display.getYRot()), (float)Math.toRadians(display.getXRot()), 0);
                var offset = orientation.transform(new org.joml.Vector3f(transform.getTranslation()));
                var bulletAxis = orientation.transform(transform.getMatrix().transformDirection(new org.joml.Vector3f(0, 1, 0))).normalize();
                Vec3 aim = arrow.getDeltaMovement().normalize();
                h.assertTrue(new Vec3(bulletAxis.x, bulletAxis.y, bulletAxis.z).dot(aim) > 0.99999,
                    "Bullet long axis follows trajectory: " + direction + " pitch=" + pitch);
                h.assertTrue(display.saveWithoutId(new CompoundTag()).getInt("interpolation_duration") == 0,
                    "Bullet must align immediately, not drift for its eight-tick lifetime");
                for (int tick = 0; tick < 4; tick++) {
                    arrow.setPos(arrow.position().add(arrow.getDeltaMovement()));
                    arrow.positionRider(display);
                    Vec3 visibleCenter = display.position().add(offset.x, offset.y, offset.z);
                    // Vanilla local coordinates use a sine lookup table; allow <0.1 mm of numerical error.
                    h.assertTrue(visibleCenter.distanceTo(arrow.position()) < 1e-4,
                        "Bullet model origin must follow arrow exactly: " + direction + " pitch=" + pitch
                        + " offset=" + visibleCenter.subtract(arrow.position()));
                }
                h.assertTrue(h.getLevel().getEntities(EntityType.MARKER,
                    entity -> entity.getTags().contains("McmBulletVisualOffset")).isEmpty(),
                    "No offset helper marker may remain after a shot");
                h.assertTrue(arrow.getOwner() == shooter && arrow.isNoGravity()
                    && Math.abs(arrow.getDeltaMovement().length() - 7) < 1e-6,
                    "Visual alignment must preserve owner, straight trajectory and speed");
                display.discard(); arrow.discard();
            }
        }
        h.succeed();
    }


}
