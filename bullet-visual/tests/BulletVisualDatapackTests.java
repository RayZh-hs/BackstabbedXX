package gravity_changer.test;

import gravity_changer.api.GravityChangerAPI;
import net.minecraft.core.Direction;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.*;
import net.minecraft.server.level.ServerEntity;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Display;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

@net.neoforged.fml.common.EventBusSubscriber(modid="gravity_changer", bus=net.neoforged.fml.common.EventBusSubscriber.Bus.MOD)
@PrefixGameTestTemplate(false)
public final class BulletVisualDatapackTests {
    @net.neoforged.bus.api.SubscribeEvent
    public static void register(net.neoforged.neoforge.event.RegisterGameTestsEvent event) {
        event.register(BulletVisualDatapackTests.class);
    }

    private static void command(GameTestHelper h, Entity executor, String command) {
        // try_fire changes executor to the arrow, but retains the shooter's command position.
        h.getLevel().getServer().getCommands().performPrefixedCommand(
            h.getLevel().getServer().createCommandSourceStack().withEntity(executor)
                .withLevel(h.getLevel()).withPosition(h.absoluteVec(new Vec3(8, 8, 8)))
                .withRotation(executor.getRotationVector()).withPermission(2).withSuppressedOutput(), command);
    }

    private record Shot(Arrow arrow, Display.ItemDisplay display) {}

    private static Shot fire(GameTestHelper h, Entity shooter) {
        shooter.addTag("queued");
        command(h, shooter, "scoreboard objectives add GameRules dummy");
        command(h, shooter, "scoreboard players set $ammo GameRules 0");
        var spawned = new java.util.ArrayList<Entity>();
        var mountedVisible = new java.util.ArrayList<Entity>();
        var spawnData = new java.util.HashMap<Entity, CompoundTag>();
        java.util.function.Consumer<net.neoforged.neoforge.event.entity.EntityJoinLevelEvent> observer = event -> {
            Entity entity = event.getEntity();
            spawned.add(entity);
            if (entity instanceof Display.ItemDisplay) spawnData.put(entity, entity.saveWithoutId(new CompoundTag()));
            if (entity instanceof Display.ItemDisplay && entity.isPassenger()
                && entity.saveWithoutId(new CompoundTag()).getCompound("item").contains("id")) mountedVisible.add(entity);
        };
        net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(observer);
        try {
            command(h, shooter, "function mcm:extensions/gun/try_fire");
        } finally {
            net.neoforged.neoforge.common.NeoForge.EVENT_BUS.unregister(observer);
        }
        h.assertTrue(mountedVisible.isEmpty(), "Visible bullet must never spawn as a passenger: client misses same-tick dismount");
        var arrow = spawned.stream().filter(e -> e instanceof Arrow).map(e -> (Arrow)e).findFirst().orElseThrow();
        var display = spawned.stream().filter(e -> e instanceof Display.ItemDisplay && e.getTags().contains("BulletDeco") && !e.isRemoved())
            .map(e -> (Display.ItemDisplay)e).findFirst().orElseThrow();
        var initial = spawnData.get(display);
        var initialPos = initial.getList("Pos", 6);
        h.assertTrue(new Vec3(initialPos.getDouble(0), initialPos.getDouble(1), initialPos.getDouble(2))
            .distanceTo(arrow.position()) < 1e-6, "First spawn packet must originate at the true muzzle");
        h.assertTrue(initial.get("Rotation").equals(display.saveWithoutId(new CompoundTag()).get("Rotation")),
            "Final orientation must be supplied before the client sees the entity");
        h.assertTrue(arrow.getPassengers().isEmpty(), "Orientation template must be removed before shot returns");
        return new Shot(arrow, display);
    }

    @GameTest(template = "empty", templateNamespace = "gravity_changer")
    public static void vanillaSameTickDismountLeavesGhostPassenger(GameTestHelper h) {
        var arrow = h.spawn(EntityType.ARROW, 8, 8, 8);
        var display = h.spawn(EntityType.ITEM_DISPLAY, 8, 8, 8);
        display.startRiding(arrow, true);
        var packets = new java.util.ArrayList<Packet<?>>();
        var arrowTracker = new ServerEntity(h.getLevel(), arrow, 20, true, packets::add);
        var displayTracker = new ServerEntity(h.getLevel(), display, 1, true, packets::add);
        var acceptor = new net.neoforged.neoforge.network.bundle.PacketAndPayloadAcceptor<ClientGamePacketListener>(packets::add);
        arrowTracker.sendPairingData(null, acceptor);
        displayTracker.sendPairingData(null, acceptor);
        display.stopRiding();
        arrowTracker.sendChanges();
        displayTracker.sendChanges();
        int[] clientPassengers = new int[0];
        for (var packet : packets) {
            if (packet instanceof ClientboundSetPassengersPacket p && p.getVehicle() == arrow.getId()) {
                clientPassengers = p.getPassengers();
                System.out.println("BULLET_PASSENGER_PACKET " + java.util.Arrays.toString(clientPassengers));
            }
        }
        System.out.println("BULLET_DISMOUNT_REPRO serverPassenger=" + display.isPassenger()
            + " clientPassengers=" + java.util.Arrays.toString(clientPassengers));
        h.assertTrue(!display.isPassenger() && clientPassengers.length == 1 && clientPassengers[0] == display.getId(),
            "Reproduce vanilla same-tick dismount desync; visible bullets must bypass this sequence");
        arrow.discard(); display.discard();
        h.succeed();
    }

    @GameTest(template = "empty", templateNamespace = "gravity_changer")
    public static void vanillaVelocityPacketBendsObliqueBullet(GameTestHelper h) {
        Vec3 actual = Vec3.directionFromRotation(0, 31).scale(7);
        var spawn = new ClientboundAddEntityPacket(1, java.util.UUID.randomUUID(), 0, 0, 0,
            0, 31, EntityType.ARROW, 0, actual, 0);
        var motion = new ClientboundSetEntityMotionPacket(1, actual);
        Vec3 received = new Vec3(spawn.getXa(), spawn.getYa(), spawn.getZa());
        double angle = Math.toDegrees(Math.acos(received.normalize().dot(actual.normalize())));
        h.assertTrue(angle > 10, "Real spawn packet bends yaw=31 shot by more than ten degrees: " + angle);
        h.assertTrue(received.equals(new Vec3(motion.getXa(), motion.getYa(), motion.getZa())),
            "Both spawn and subsequent motion packets clamp velocity");
        h.assertTrue(Math.abs(received.z) == 3.9 && actual.length() > received.length(),
            "Network component cap, not a gravity or model-center error");
        System.out.println("BULLET_PACKET_REPRO actual=" + actual + " received=" + received + " angle=" + angle);
        h.succeed();
    }

    @GameTest(template = "empty", templateNamespace = "gravity_changer", timeoutTicks = 200)
    public static void bulletVisualPositionPacketsFollowTrajectory(GameTestHelper h) {
        var shooter = h.spawn(EntityType.PIG, 8, 8, 8);
        for (Direction direction : Direction.values()) {
            GravityChangerAPI.setBaseGravityDirection(shooter, direction);
            GravityChangerAPI.getGravityComponent(shooter).applyGravityChange();
            for (float yaw : new float[]{0, 17, 31, 45, 90, 137, -63, -151}) {
                for (float pitch : new float[]{-75, 0, 43}) {
                    shooter.setYRot(yaw); shooter.setXRot(pitch);
                    var shot = fire(h, shooter);
                    var arrow = shot.arrow(); var display = shot.display();
                    String context = direction + " yaw=" + yaw + " pitch=" + pitch;
                    h.assertTrue(!display.isPassenger(), "Visual must not use client-clamped arrow prediction: " + context);
                    h.assertTrue(display.position().distanceTo(arrow.position()) < 1e-6,
                        "Initial visual uses arrow position, not caller/shooter position: " + context);
                    var saved = display.saveWithoutId(new CompoundTag());
                    var transform = com.mojang.math.Transformation.CODEC.parse(net.minecraft.nbt.NbtOps.INSTANCE,
                        saved.get("transformation")).result().orElseThrow();
                    h.assertTrue(transform.getTranslation().length() < 1e-6, "No seat offset after dismount");
                    var orientation = new org.joml.Quaternionf().rotationYXZ(
                        (float)Math.toRadians(-display.getYRot()), (float)Math.toRadians(display.getXRot()), 0);
                    var axis = orientation.transform(transform.getMatrix().transformDirection(new org.joml.Vector3f(0, 1, 0))).normalize();
                    Vec3 aim = arrow.getDeltaMovement().normalize();
                    h.assertTrue(new Vec3(axis.x, axis.y, axis.z).dot(aim) > 0.99999, "Visual orientation: " + context);
                    h.assertTrue(saved.getInt("interpolation_duration") == 0 && saved.getInt("teleport_duration") == 1,
                        "Immediate transform and one-tick position interpolation");
                    var packets = new java.util.ArrayList<Packet<?>>();
                    var tracker = new ServerEntity(h.getLevel(), display, 1, true, packets::add);
                    var spawn = (ClientboundAddEntityPacket)display.getAddEntityPacket(tracker);
                    h.assertTrue(spawn.getXa() == 0 && spawn.getYa() == 0 && spawn.getZa() == 0,
                        "Display spawn does not transmit clamped projectile velocity");
                    var codec = new VecDeltaCodec();
                    codec.setBase(new Vec3(spawn.getX(), spawn.getY(), spawn.getZ()));
                    Vec3 origin = arrow.position(); Vec3 lastTarget = origin;
                    for (int tick = 0; tick < 6; tick++) {
                        arrow.setPos(arrow.position().add(arrow.getDeltaMovement()));
                        command(h, display, "function mcm:extensions/gun/sync_visual with entity @s item.components.\"minecraft:custom_data\"");
                        h.assertTrue(display.position().distanceTo(arrow.position()) < 1e-6, "Server target: " + context
                            + " tick=" + tick + " arrow=" + arrow.position() + " display=" + display.position()
                            + " displayRemoved=" + display.isRemoved() + " arrowRemoved=" + arrow.isRemoved());
                        packets.clear(); tracker.sendChanges();
                        boolean moved = false;
                        for (var packet : packets) {
                            Vec3 target = null;
                            if (packet instanceof ClientboundMoveEntityPacket move && move.hasPosition()) {
                                target = codec.decode(move.getXa(), move.getYa(), move.getZa());
                            } else if (packet instanceof ClientboundEntityPositionSyncPacket sync) {
                                target = sync.values().position();
                            }
                            if (target != null) {
                                moved = true;
                                h.assertTrue(target.distanceTo(arrow.position()) < .0005, "Client receives true endpoint: " + context);
                                for (double t : new double[]{0, .25, .5, .75, 1}) {
                                    var delta = lastTarget.lerp(target, t).subtract(origin);
                                    h.assertTrue(delta.subtract(aim.scale(delta.dot(aim))).length() < .0005,
                                        "Rendered segment stays on trajectory: " + context);
                                }
                                codec.setBase(target); lastTarget = target;
                            }
                        }
                        h.assertTrue(moved, "Every tick must send a position packet: " + context);
                        arrow.setDeltaMovement(arrow.getDeltaMovement().scale(.99));
                    }
                    h.assertTrue(arrow.getOwner() == shooter && arrow.isNoGravity()
                        && Math.abs(arrow.getDeltaMovement().length() - 7 * Math.pow(.99, 6)) < 1e-5,
                        "Visual updates preserve ownership, velocity and no-gravity");
                    display.discard(); arrow.discard();
                }
            }
        }
        h.succeed();
    }

    @GameTest(template = "empty", templateNamespace = "gravity_changer")
    public static void concurrentVisualsFollowOnlyTheirOwnArrow(GameTestHelper h) {
        var shooter = h.spawn(EntityType.PIG, 8, 8, 8);
        var a = fire(h, shooter); var b = fire(h, shooter);
        a.arrow().setPos(a.arrow().position().add(5, 0, 0));
        b.arrow().setPos(b.arrow().position().add(-5, 0, 0));
        for (var shot : new Shot[]{a, b}) {
            command(h, shot.display(), "function mcm:extensions/gun/sync_visual with entity @s item.components.\"minecraft:custom_data\"");
            h.assertTrue(shot.display().position().distanceTo(shot.arrow().position()) < 1e-6,
                "Coincident shots are linked by full UUID, not nearest distance");
        }
        a.arrow().discard();
        command(h, shooter, "scoreboard objectives add gundelay dummy");
        command(h, shooter, "function mcm:game/items/gun/shoot");
        h.assertTrue(a.display().isRemoved() && !b.display().isRemoved(), "Only the missing arrow's visual is removed");
        command(h, b.arrow(), "scoreboard players set @s gundelay 7");
        command(h, shooter, "function mcm:game/items/gun/shoot");
        h.assertTrue(b.arrow().isRemoved() && b.display().isRemoved(), "Range expiry cleans up its paired visual in the same tick");
        h.succeed();
    }
}
