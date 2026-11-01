package backstabbed.modetest;

import com.mojang.authlib.GameProfile;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import net.minecraft.client.Minecraft;
import net.minecraft.network.Connection;
import io.netty.channel.Channel;
import io.netty.channel.embedded.EmbeddedChannel;
import java.net.SocketAddress;
import java.net.InetSocketAddress;
import net.minecraft.network.PacketListener;
import net.minecraft.network.ProtocolInfo;
import net.minecraft.network.PacketSendListener;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.PacketFlow;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ClientInformation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.network.CommonListenerCookie;
import net.minecraft.server.network.ServerGamePacketListenerImpl;
import net.minecraft.world.item.Items;
import net.minecraft.world.scores.ScoreHolder;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

@Mod("backstabbed_mode_test")
public final class ModeRegression {
    private int ticks;
    private boolean finished;
    private final List<String> results = new ArrayList<>();
    private final Path output = Path.of(System.getenv("BACKSTABBED_MODE_TEST_OUTPUT"));
    public ModeRegression() { NeoForge.EVENT_BUS.addListener(this::tick); }
    private void cmd(MinecraftServer s, String c) {
        s.getCommands().performPrefixedCommand(s.createCommandSourceStack().withPermission(4).withSuppressedOutput(), c);
    }
    private int score(MinecraftServer s, String who, String objective) {
        var value = s.getScoreboard().getPlayerScoreInfo(ScoreHolder.forNameOnly(who), s.getScoreboard().getObjective(objective));
        return value == null ? 0 : value.value();
    }
    private void check(boolean ok, String label) {
        if (!ok) throw new AssertionError(label);
        results.add(label);
        System.out.println("MODE PASS: " + label);
    }
    private ServerPlayer bot(MinecraftServer s, String name) {
        var profile = new GameProfile(UUID.randomUUID(), name);
        var p = new ServerPlayer(s, s.overworld(), profile, ClientInformation.createDefault());
        var cookie = CommonListenerCookie.createInitial(profile, false);
        p.connection = new IdleListener(s, p, cookie);
        // The public player list is immutable; bypass login negotiation for these
        // server-only fixtures, whose listener discards mod payloads.
        try {
            var field = net.minecraft.server.players.PlayerList.class.getDeclaredField("players");
            field.setAccessible(true);
            @SuppressWarnings("unchecked")
            var players = (List<ServerPlayer>) field.get(s.getPlayerList());
            players.add(p);
        } catch (ReflectiveOperationException e) { throw new RuntimeException(e); }
        s.overworld().addNewPlayer(p);
        return p;
    }
    private void start(MinecraftServer s, int mode) {
        cmd(s, "function mcm:modes/reset");
        cmd(s, "clear @a");
        cmd(s, "effect clear @a");
        for (String tag : List.of("murderer", "innocent", "gunner", "spectating", "force_murderer", "lostGun")) cmd(s,"tag @a remove " + tag);
        cmd(s, "tag @a add queued");
        cmd(s, "gamemode adventure @a");
        cmd(s, "scoreboard players set @a dead 0");
        cmd(s, "scoreboard players set $mode CmdData " + mode);
        cmd(s, "scoreboard players set $gamestate CmdData 1");
        cmd(s, "scoreboard players set $graceperiod CmdData 0");
        cmd(s, "scoreboard players set $gametimer CmdData 1200");
        cmd(s, "scoreboard players set $murderers GameRules 1");
        cmd(s, "scoreboard players set $murderWin CmdData 0");
        cmd(s, "scoreboard players set $innocentWin CmdData 0");
        cmd(s, "scoreboard players set $selectedMap CmdData 0");
        cmd(s, "function mcm:game/pick_roles");
    }
    private List<ServerPlayer> team(MinecraftServer s, int team) {
        return s.getPlayerList().getPlayers().stream().filter(p -> score(s,p.getScoreboardName(),"bb_team") == team).toList();
    }
    private ServerPlayer gunner(MinecraftServer s, int team) {
        return team(s,team).stream().filter(p -> p.getTags().contains("gunner")).findFirst().orElseThrow();
    }
    private ServerPlayer runner(MinecraftServer s, int team) {
        return team(s,team).stream().filter(p -> !p.getTags().contains("gunner")).findFirst().orElseThrow();
    }
    private void call(MinecraftServer s, ServerPlayer p, String function) {
        cmd(s, "execute as " + p.getScoreboardName() + " at @s run function " + function);
    }
    private void hit(MinecraftServer s, ServerPlayer attacker, ServerPlayer victim) {
        victim.setLastHurtByMob(attacker);
        call(s,victim,"mcm:game/player_hit");
    }
    private void run(MinecraftServer s, ServerPlayer human) {
        for (int i=1; i<=3; i++) bot(s,"ModeBot"+i);
        cmd(s,"summon marker 0 2 70 {Tags:[\"PlayerSpawn\"]}");
        cmd(s,"data remove storage mcm:options options.ext.mode");
        cmd(s,"function mcm:extensions/options/init");
        check(score(s,"$mode","GameRules")==0,"missing saved option defaults to Classic");
        cmd(s,"scoreboard players set $gamestate CmdData 0");
        cmd(s,"data modify storage mcm:options options.locked set value 0");
        cmd(s,"scoreboard players set " + human.getScoreboardName()+" mcm_options 16");
        call(s,human,"mcm:extensions/options/change");
        check(score(s,"$mode","GameRules")==1,"second-floor menu selects Gunner");
        cmd(s,"scoreboard players set $gamestate CmdData 1");
        cmd(s,"scoreboard players set " + human.getScoreboardName()+" mcm_options 17");
        call(s,human,"mcm:extensions/options/change");
        check(score(s,"$mode","GameRules")==1,"active round rejects mode changes");
        start(s,1);
        check(team(s,1).size()==2 && team(s,2).size()==2,"four players split into balanced teams");
        check(s.getPlayerList().getPlayers().stream().filter(p->p.getTags().contains("gunner")).count()==2,"exactly one initial gunner per team");
        cmd(s,"function mcm:game/loops/ingame");
        check(score(s,"$gamestate","CmdData")==1,"full Gunner loop bypasses Classic no-murderer victory");
        var red=gunner(s,1); var blue=gunner(s,2); var mate=runner(s,1);
        check(red.getInventory().countItem(Items.WARPED_FUNGUS_ON_A_STICK)==1,"initial gunner receives a real gun");
        hit(s,red,mate);
        check(!mate.getTags().contains("spectating"),"teammate weapon hit is ignored");
        hit(s,blue,mate);
        check(mate.getTags().contains("spectating") && score(s,mate.getScoreboardName(),"bb_respawn")==60,"enemy hit starts three-second respawn");
        for(int i=0;i<59;i++) cmd(s,"function mcm:modes/tick");
        check(mate.getTags().contains("spectating"),"respawn waits all sixty ticks");
        cmd(s,"function mcm:modes/tick");
        check(!mate.getTags().contains("spectating") && !mate.isSpectator() && score(s,mate.getScoreboardName(),"dead")==0,"runner returns to adventure and clears death state");
        hit(s,blue,mate);
        check(!mate.getTags().contains("spectating"),"respawn protection blocks immediate weapon kill");
        cmd(s,"give " + mate.getScoreboardName()+" netherite_scrap 9");
        call(s,mate,"mcm:game/items/scrap_function");
        check(!mate.getTags().contains("gunner"),"nine scraps cannot promote a gunner");
        cmd(s,"give " + mate.getScoreboardName()+" netherite_scrap 3");
        call(s,mate,"mcm:game/items/scrap_function");
        check(mate.getTags().contains("gunner") && mate.getInventory().countItem(Items.NETHERITE_SCRAP)==2,"promotion costs exactly ten scraps and preserves surplus");
        call(s,red,"mcm:game/playerdeath");
        cmd(s,"function mcm:modes/tick");
        check(score(s,"$gamestate","CmdData")==1,"promoted gunner keeps team alive after initial gunner dies");
        check(score(s,red.getScoreboardName(),"bb_respawn")==0,"dead gunner never respawns");
        call(s,mate,"mcm:game/playerdeath");
        cmd(s,"function mcm:modes/tick");
        check(score(s,"$red_out","CmdData")==1 && score(s,"$winner","CmdData")==2,"last gunner death eliminates team and awards opponent victory");
        start(s,1);
        red=gunner(s,1); mate=runner(s,1);
        call(s,mate,"mcm:game/playerdeath");
        call(s,red,"mcm:game/playerdeath");
        cmd(s,"function mcm:modes/tick");
        check(score(s,mate.getScoreboardName(),"bb_respawn")==0,"losing last gunner cancels pending respawns");
        start(s,2);
        check(s.getPlayerList().getPlayers().stream().allMatch(p->p.getTags().contains("murderer") && p.getInventory().countItem(Items.SNOWBALL)>0),"Killer gives everyone the killer role and knife");
        cmd(s,"function mcm:game/loops/ingame");
        check(score(s,"$gamestate","CmdData")==1,"full Killer loop bypasses Classic no-innocent victory");
        var reds=team(s,1); var blues=team(s,2);
        hit(s,reds.get(0),reds.get(1));
        check(!reds.get(1).getTags().contains("spectating"),"Killer teammate hit is ignored");
        hit(s,blues.get(0),reds.get(0));
        cmd(s,"function mcm:modes/tick");
        check(reds.get(0).getTags().contains("spectating") && score(s,"$gamestate","CmdData")==1,"Killer enemy hit kills without ending a surviving team");
        hit(s,blues.get(0),reds.get(1));
        cmd(s,"function mcm:modes/tick");
        check(score(s,"$winner","CmdData")==2,"Killer ends when all opposing team members die");
        start(s,2);
        cmd(s,"execute as @a run function mcm:game/playerdeath");
        cmd(s,"function mcm:modes/tick");
        check(score(s,"$red_out","CmdData")==1 && score(s,"$blue_out","CmdData")==1 && score(s,"$winner","CmdData")==0,"simultaneous team elimination draws");
        start(s,1);
        cmd(s,"scoreboard players set $gametimer CmdData 1");
        cmd(s,"function mcm:game/loops/game_timer");
        cmd(s,"function mcm:modes/tick");
        check(score(s,"$gamestate","CmdData")==2 && score(s,"$winner","CmdData")==0 && score(s,"$innocentWin","CmdData")==0,"team-mode timeout draws without Classic victory");
        start(s,1);
        var disconnected=gunner(s,1);
        disconnected.removeTag("queued");
        cmd(s,"function mcm:modes/tick");
        check(score(s,"$red_out","CmdData")==1,"absent last gunner eliminates their team");
        disconnected.addTag("queued");
        cmd(s,"function mcm:modes/tick");
        check(disconnected.getTags().contains("spectating"),"returning gunner cannot revive eliminated team");
        cmd(s,"scoreboard players set $gameEndTimer CmdData 200");
        cmd(s,"function mcm:game/loops/gameend");
        check(team(s,2).stream().allMatch(p->p.getTags().contains("WonLast")),"team victory tags winning team after Classic result cleanup");
        start(s,0);
        check(s.getPlayerList().getPlayers().stream().filter(p->p.getTags().contains("murderer")).count()==1,"Classic still assigns one murderer");
        check(s.getPlayerList().getPlayers().stream().filter(p->p.getTags().contains("gunner")).count()==1,"Classic still assigns one gunner");
        cmd(s,"execute as @a[tag=murderer] run function mcm:game/playerdeath");
        cmd(s,"function mcm:game/loops/ingame");
        check(score(s,"$innocentWin","CmdData")==1 && score(s,"$classic_red_out","CmdData")==1,"Classic victory is preserved with elimination announcement");
    }
    private void tick(ServerTickEvent.Post event) {
        if(finished) return;
        var s=event.getServer();
        var p=s.getPlayerList().getPlayerByName("BackstabbedDev");
        if(p==null || ++ticks<80) return;
        try { run(s,p); finish(null); }
        catch(Throwable t) { t.printStackTrace(); finish(t); }
    }
    private void finish(Throwable failure) {
        finished=true;
        try { Files.writeString(output,(failure==null?"PASS\n":"FAIL: "+failure+"\n")+String.join("\n",results)+"\n"); }
        catch(Exception e) { e.printStackTrace(); }
        Minecraft.getInstance().execute(()->Minecraft.getInstance().stop());
    }
    private static final class IdleListener extends ServerGamePacketListenerImpl {
        IdleListener(MinecraftServer s,ServerPlayer p,CommonListenerCookie cookie) {
            super(s,new IdleConnection(),p,cookie);
        }
        @Override public void tick() {}
        @Override public void send(Packet<?> packet) {}
        @Override public void send(Packet<?> packet,PacketSendListener listener) {}
    }
    private static final class IdleConnection extends Connection {
        private final Channel channel = new EmbeddedChannel();
        IdleConnection() { super(PacketFlow.SERVERBOUND); }
        @Override public Channel channel() { return channel; }
        @Override public SocketAddress getRemoteAddress() { return new InetSocketAddress("127.0.0.1",0); }
        @Override public boolean isMemoryConnection() { return true; }
        @Override public boolean isConnected() { return true; }
        @Override public <T extends PacketListener> void setupInboundProtocol(ProtocolInfo<T> protocol,T listener) {}
        @Override public void setupOutboundProtocol(ProtocolInfo<?> protocol) {}
        @Override public void send(Packet<?> p) {}
        @Override public void send(Packet<?> p,PacketSendListener l) {}
        @Override public void send(Packet<?> p,PacketSendListener l,boolean flush) {}
        @Override public void flushChannel() {}
    }
}
