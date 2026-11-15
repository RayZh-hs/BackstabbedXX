package gravity_changer.test;

import java.util.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.*;
import net.minecraft.world.effect.*;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

@net.neoforged.fml.common.EventBusSubscriber(modid="gravity_changer",bus=net.neoforged.fml.common.EventBusSubscriber.Bus.MOD)
@PrefixGameTestTemplate(false)
public final class LobbySpeedTests {
    @net.neoforged.bus.api.SubscribeEvent public static void register(net.neoforged.neoforge.event.RegisterGameTestsEvent e){e.register(LobbySpeedTests.class);}
    @GameTest(template="empty",templateNamespace="gravity_changer",batch="lobby_speed",timeoutTicks=100)
    public static void lobbyOnlySpeedAndPriority(GameTestHelper h){
        var level=h.getLevel();var lobby=player(level,"LobbySpeed");var arena=player(level,"ArenaSpeed");
        var nether=player(level.getServer().getLevel(net.minecraft.world.level.Level.NETHER),"NetherSpeed");
        var online=players(level);online.add(lobby);online.add(arena);online.add(nether);
        try {
            lobby.setPos(0,1,70);arena.setPos(1000,64,1000);nether.setPos(0,1,70);
            lobby.addTag("queued");
            command(lobby,"function mcm:lobby/speed");
            var effect=lobby.getEffect(MobEffects.MOVEMENT_SPEED);
            h.assertTrue(effect!=null && effect.getAmplifier()==1 && effect.getDuration()==20,"Lobby players receive Speed II for one second");
            h.assertTrue(!arena.hasEffect(MobEffects.MOVEMENT_SPEED) && !nether.hasEffect(MobEffects.MOVEMENT_SPEED),"Arena and other dimensions are excluded");
            lobby.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED,100,3));
            command(lobby,"function mcm:lobby/speed");
            h.assertTrue(lobby.getEffect(MobEffects.MOVEMENT_SPEED).getAmplifier()==3,"Stronger adrenaline speed is preserved");
            lobby.removeEffect(MobEffects.MOVEMENT_SPEED);
            command(lobby,"scoreboard objectives add CmdData dummy");
            command(lobby,"scoreboard players set $gamestate CmdData 1");
            command(lobby,"function mcm:lobby/speed");
            h.assertTrue(lobby.getEffect(MobEffects.MOVEMENT_SPEED).getAmplifier()==1,"A player still in the lobby is accelerated during another player's game");
            lobby.setPos(1000,64,1000);
            // Tick the actual effect instance to expiry without advancing unrelated round logic.
            var leaving=lobby.getEffect(MobEffects.MOVEMENT_SPEED);
            for(int i=0;i<19;i++) h.assertTrue(leaving.tick(lobby,()->{}),"Speed remains only for its short remaining duration");
            h.assertTrue(!leaving.tick(lobby,()->{}),"Lobby speed expires after 20 ticks outside");
            lobby.removeEffect(MobEffects.MOVEMENT_SPEED);
            command(lobby,"function mcm:lobby/speed");
            h.assertTrue(!lobby.hasEffect(MobEffects.MOVEMENT_SPEED),"Leaving the lobby prevents refreshing speed");
            System.out.println("LOBBY_SPEED_PASS scope, Speed II, dimension guard, effect priority and expiry");
        }finally{
            command(lobby,"scoreboard players set $gamestate CmdData 0");
            for(var p:List.of(lobby,arena,nether)){online.remove(p);p.discard();}
        }
        h.succeed();
    }
    private static void command(ServerPlayer p,String s){p.getServer().getCommands().performPrefixedCommand(p.getServer().createCommandSourceStack().withEntity(p).withLevel((ServerLevel)p.level()).withPosition(p.position()).withPermission(4).withSuppressedOutput(),s);}
    private static ServerPlayer player(ServerLevel l,String name){var profile=new GameProfile(UUID.randomUUID(),name);var p=new ServerPlayer(l.getServer(),l,profile,ClientInformation.createDefault());p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(l.getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p,net.minecraft.server.network.CommonListenerCookie.createInitial(profile,false)){
        @Override public boolean hasChannel(net.minecraft.resources.ResourceLocation c){return false;}
        @Override public void send(net.minecraft.network.protocol.Packet<?> p){}
        @Override public void send(net.minecraft.network.protocol.Packet<?> p,net.minecraft.network.PacketSendListener s){}
    };p.setClientLoaded(true);p.initInventoryMenu();l.addNewPlayer(p);return p;}
    @SuppressWarnings("unchecked") private static List<ServerPlayer> players(ServerLevel l){try{var f=net.minecraft.server.players.PlayerList.class.getDeclaredField("players");f.setAccessible(true);return (List<ServerPlayer>)f.get(l.getServer().getPlayerList());}catch(Exception e){throw new RuntimeException(e);}}
}
