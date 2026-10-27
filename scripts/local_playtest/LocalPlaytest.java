package backstabbed.local;

import com.mojang.authlib.GameProfile;
import io.netty.channel.Channel;
import io.netty.channel.embedded.EmbeddedChannel;
import java.net.InetSocketAddress;
import java.net.SocketAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import net.minecraft.network.Connection;
import net.minecraft.network.PacketListener;
import net.minecraft.network.PacketSendListener;
import net.minecraft.network.ProtocolInfo;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.PacketFlow;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ClientInformation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.network.CommonListenerCookie;
import net.minecraft.server.network.ServerGamePacketListenerImpl;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.storage.LevelResource;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/** Loaded only in the launcher's disposable game directory. */
@Mod("backstabbed_local")
public final class LocalPlaytest {
    private static final String BOT_TAG = "backstabbed_local_dummy";
    private static final List<String> NAMES = List.of("PlaytestDummy1", "PlaytestDummy2", "PlaytestDummy3");

    public LocalPlaytest() {
        NeoForge.EVENT_BUS.addListener(this::tick);
    }

    private void tick(ServerTickEvent.Post event) {
        MinecraftServer server = event.getServer();
        if (server.isDedicatedServer()
                || !Files.exists(server.getWorldPath(LevelResource.ROOT).resolve(".backstabbed-local"))) {
            return;
        }
        var players = server.getPlayerList();
        var humans = players.getPlayers().stream().filter(p -> !p.getTags().contains(BOT_TAG)).toList();
        if (humans.isEmpty() || server.getScoreboard().getObjective("CmdData") == null) {
            return;
        }
        for (String name : NAMES) {
            ServerPlayer dummy = players.getPlayerByName(name);
            if (dummy == null) {
                UUID uuid = UUID.nameUUIDFromBytes(("OfflinePlayer:" + name).getBytes(StandardCharsets.UTF_8));
                GameProfile profile = new GameProfile(uuid, name);
                dummy = new ServerPlayer(server, server.overworld(), profile, ClientInformation.createDefault());
                dummy.addTag(BOT_TAG);
                var cookie = CommonListenerCookie.createInitial(profile, false);
                players.placeNewPlayer(new IdleConnection(), dummy, cookie);
                dummy.connection = new IdleListener(server, dummy, cookie);
                for (ServerPlayer human : humans) {
                    players.op(human.getGameProfile());
                    human.sendSystemMessage(Component.literal("Local playtest: " + name + " joined. Select an arena and queue normally."));
                }
            }
            if (dummy.isDeadOrDying()) {
                dummy = players.respawn(dummy, false, Entity.RemovalReason.KILLED);
                dummy.connection.player = dummy;
            }
            if (dummy.getTags().contains("first_join") && !dummy.getTags().contains("local_positioned")) {
                // Keep the lobby entrance clear after the map's first-join teleport.
                dummy.teleportTo(server.overworld(), 4 - NAMES.indexOf(name), 1, 77, Set.of(), 180, 0, false);
                dummy.addTag("local_positioned");
            }
            // Network-free players need the update normally driven by their connection.
            dummy.doTick();
            var source = dummy.createCommandSourceStack().withPermission(4).withSuppressedOutput();
            server.getCommands().performPrefixedCommand(source,
                    "execute if score $gamestate CmdData matches 0 run tag @s add autoqueue");
            server.getCommands().performPrefixedCommand(source,
                    "execute if score $gamestate CmdData matches 0 run tag @s remove afk");
            server.getCommands().performPrefixedCommand(source,
                    "execute if score $gamestate CmdData matches 0 unless entity @s[tag=queued] run function mcm:lobby/queueing/try_queue");
        }
    }

    /** Use PlayerList's regular join path, discarding packets intended for the idle client. */
    private static final class IdleConnection extends Connection {
        private final Channel channel = new EmbeddedChannel();

        IdleConnection() { super(PacketFlow.SERVERBOUND); }

        @Override public Channel channel() { return channel; }
        @Override public SocketAddress getRemoteAddress() { return new InetSocketAddress("127.0.0.1", 0); }
        @Override public boolean isMemoryConnection() { return true; }
        @Override public boolean isConnected() { return true; }
        @Override public <T extends PacketListener> void setupInboundProtocol(ProtocolInfo<T> protocol, T listener) {}
        @Override public void setupOutboundProtocol(ProtocolInfo<?> protocol) {}
        @Override public void send(Packet<?> packet) {}
        @Override public void send(Packet<?> packet, PacketSendListener listener) {}
        @Override public void send(Packet<?> packet, PacketSendListener listener, boolean flush) {}
        @Override public void flushChannel() {}
    }

    private static final class IdleListener extends ServerGamePacketListenerImpl {
        IdleListener(MinecraftServer server, ServerPlayer player, CommonListenerCookie cookie) {
            super(server, new IdleConnection(), player, cookie);
        }

        // There is no client to send keepalives, movement or teleport acknowledgements.
        @Override public void tick() {}

        // Discard here, before NeoForge validates custom payload channels. These
        // players have no client and never negotiate mod networking channels.
        @Override public void send(Packet<?> packet) {}
        @Override public void send(Packet<?> packet, PacketSendListener listener) {}
    }
}
