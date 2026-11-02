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
        p.setClientLoaded(true);
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
        cmd(s, "kill @e[type=item]");
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
        cmd(s, "scoreboard players set $kill_reward GameRules 0");
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
    private void option(MinecraftServer s, ServerPlayer p, int choice) {
        cmd(s,"function mcm:extensions/tick");
        s.getCommands().performPrefixedCommand(p.createCommandSourceStack().withPermission(0).withSuppressedOutput(),
                "trigger mcm_options set " + choice);
        cmd(s,"function mcm:extensions/tick");
    }
    private void waitForRespawn(MinecraftServer s, ServerPlayer p, int ticks, String label) {
        for(int i=0;i<ticks-1;i++) cmd(s,"function mcm:modes/tick");
        check(p.getTags().contains("spectating") && score(s,p.getScoreboardName(),"bb_respawn")==1,
                label + " waits until the final tick");
        cmd(s,"function mcm:modes/tick");
        check(!p.getTags().contains("spectating") && !p.isSpectator()
                && !p.getTags().contains("gunner") && p.getTags().contains("innocent")
                && p.getInventory().countItem(Items.WARPED_FUNGUS_ON_A_STICK)==0
                && score(s,p.getScoreboardName(),"bb_respawn")==0
                && score(s,p.getScoreboardName(),"dead")==0,
                label + " returns as an ordinary player without a gun");
    }
    private void hit(MinecraftServer s, ServerPlayer attacker, ServerPlayer victim) {
        victim.setLastHurtByMob(attacker);
        call(s,victim,"mcm:game/player_hit");
    }
    private int entities(MinecraftServer s, String selector) {
        cmd(s,"execute store result score $test_count temp if entity " + selector);
        return score(s,"$test_count","temp");
    }
    private int adrenalineDrops(MinecraftServer s) {
        return entities(s,"@e[type=item,tag=bb_kill_adrenaline]");
    }
    private void run(MinecraftServer s, ServerPlayer human) {
        for (int i=1; i<=3; i++) bot(s,"ModeBot"+i);
        cmd(s,"summon marker 0 2 70 {Tags:[\"PlayerSpawn\"]}");
        cmd(s,"data remove storage mcm:options options.ext.mode");
        cmd(s,"data remove storage mcm:options options.ext.gunner_respawn");
        cmd(s,"function mcm:extensions/options/init");
        check(score(s,"$mode","GameRules")==0,"missing saved option defaults to Classic");
        check(score(s,"$gunner_respawn","GameRules")==10 && score(s,"$gunner_respawn_ticks","GameRules")==200,
                "missing respawn setting defaults to ten seconds");
        cmd(s,"scoreboard players set $gamestate CmdData 0");
        cmd(s,"data modify storage mcm:options options.locked set value 0");
        int[] delays={3,5,10,20,30};
        for(int i=0;i<delays.length;i++) {
            option(s,human,18+i);
            check(score(s,"$gunner_respawn","GameRules")==delays[i]
                    && score(s,"$gunner_respawn_ticks","GameRules")==20*delays[i],
                    "non-operator trigger selects " + delays[i] + "-second respawn");
            cmd(s,"scoreboard players set $gunner_respawn GameRules 0");
            cmd(s,"function mcm:extensions/options/init");
            check(score(s,"$gunner_respawn","GameRules")==delays[i],
                    delays[i] + "-second setting survives option reinitialization");
        }
        for(int invalid : new int[]{-3,0,4,15,31}) {
            cmd(s,"data modify storage mcm:options options.ext.gunner_respawn set value " + invalid);
            cmd(s,"function mcm:modes/sync");
            check(score(s,"$gunner_respawn","GameRules")==10 && score(s,"$gunner_respawn_ticks","GameRules")==200,
                    "invalid respawn delay " + invalid + " falls back to ten seconds");
        }
        cmd(s,"data modify storage mcm:options options.locked set value 1");
        option(s,human,18);
        check(score(s,"$gunner_respawn","GameRules")==10,"locked lobby rejects respawn delay changes");
        cmd(s,"data modify storage mcm:options options.locked set value 0");
        cmd(s,"scoreboard players set " + human.getScoreboardName()+" mcm_options 16");
        call(s,human,"mcm:extensions/options/change");
        check(score(s,"$mode","GameRules")==1,"second-floor menu selects Gunner");
        cmd(s,"scoreboard players set $gamestate CmdData 1");
        cmd(s,"scoreboard players set " + human.getScoreboardName()+" mcm_options 17");
        call(s,human,"mcm:extensions/options/change");
        check(score(s,"$mode","GameRules")==1,"active round rejects mode changes");
        cmd(s,"scoreboard players set " + human.getScoreboardName()+" mcm_options 0");
        option(s,human,18);
        check(score(s,"$gunner_respawn","GameRules")==10,"active round rejects respawn delay changes");
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
        check(mate.getTags().contains("spectating") && score(s,mate.getScoreboardName(),"bb_respawn")==200,"enemy hit starts default ten-second respawn");
        waitForRespawn(s,mate,200,"ordinary player respawn");
        hit(s,blue,mate);
        check(!mate.getTags().contains("spectating"),"respawn protection blocks immediate weapon kill");
        cmd(s,"give " + mate.getScoreboardName()+" netherite_scrap 9");
        call(s,mate,"mcm:game/items/scrap_function");
        check(!mate.getTags().contains("gunner"),"nine scraps cannot promote a gunner");
        cmd(s,"give " + mate.getScoreboardName()+" netherite_scrap 3");
        call(s,mate,"mcm:game/items/scrap_function");
        check(mate.getTags().contains("gunner") && mate.getInventory().countItem(Items.NETHERITE_SCRAP)==2,"promotion costs exactly ten scraps and preserves surplus");
        hit(s,blue,red);
        check(red.getTags().contains("spectating") && !red.getTags().contains("gunner")
                && red.getInventory().countItem(Items.WARPED_FUNGUS_ON_A_STICK)==0
                && score(s,red.getScoreboardName(),"bb_respawn")==200,
                "initial gunner loses their gun and schedules a respawn while another gunner survives");
        cmd(s,"function mcm:game/loops/ingame");
        check(score(s,"$gamestate","CmdData")==1,"promoted gunner keeps team alive after initial gunner dies");
        check(!red.getTags().contains("gunner"),"full game loop cannot restore the dead gunner role");
        call(s,red,"mcm:game/playerdeath");
        check(score(s,red.getScoreboardName(),"bb_respawn")==199,"repeated death callback cannot restart the respawn timer");
        waitForRespawn(s,red,199,"initial gunner respawn");
        cmd(s,"give " + red.getScoreboardName()+" netherite_scrap 10");
        call(s,red,"mcm:game/items/scrap_function");
        check(red.getTags().contains("gunner") && red.getInventory().countItem(Items.WARPED_FUNGUS_ON_A_STICK)==1,
                "former gunner can earn a gun again by collecting ten scrap");
        call(s,red,"mcm:game/playerdeath");
        call(s,mate,"mcm:game/playerdeath");
        cmd(s,"function mcm:modes/tick");
        check(score(s,"$red_out","CmdData")==1 && score(s,"$winner","CmdData")==2
                && score(s,red.getScoreboardName(),"bb_respawn")==0
                && score(s,mate.getScoreboardName(),"bb_respawn")==0,
                "last gunner death eliminates team, cancels former gunner respawns and awards opponent victory");
        start(s,1);
        red=gunner(s,1); mate=runner(s,1);
        call(s,mate,"mcm:game/playerdeath");
        call(s,red,"mcm:game/playerdeath");
        cmd(s,"function mcm:modes/tick");
        check(score(s,mate.getScoreboardName(),"bb_respawn")==0,"losing last gunner cancels pending respawns");
        for(int i=0;i<delays.length;i++) {
            cmd(s,"scoreboard players set $gamestate CmdData 0");
            option(s,human,18+i);
            start(s,1);
            int side=i%2+1;
            var promoted=runner(s,side);
            cmd(s,"give " + promoted.getScoreboardName()+" netherite_scrap 10");
            call(s,promoted,"mcm:game/items/scrap_function");
            check(promoted.getTags().contains("gunner"),"respawn fixture promotes a second gunner on team " + side);
            hit(s,gunner(s,side==1?2:1),promoted);
            check(promoted.getTags().contains("spectating") && score(s,promoted.getScoreboardName(),"bb_respawn")==20*delays[i],
                    "promoted gunner death uses the selected " + delays[i] + "-second delay");
            waitForRespawn(s,promoted,20*delays[i],delays[i] + "-second promoted gunner respawn");
        }
        start(s,1);
        call(s,gunner(s,1),"mcm:game/playerdeath");
        call(s,gunner(s,2),"mcm:game/playerdeath");
        cmd(s,"function mcm:modes/tick");
        check(score(s,"$red_out","CmdData")==1 && score(s,"$blue_out","CmdData")==1
                && score(s,"$winner","CmdData")==0 && entities(s,"@a[scores={bb_respawn=1..}]")==0,
                "both last gunners dying together draws and leaves no pending respawns");
        cmd(s,"scoreboard players set $gamestate CmdData 0");
        option(s,human,20);
        start(s,2);
        check(s.getPlayerList().getPlayers().stream().allMatch(p->p.getTags().contains("murderer") && p.getInventory().countItem(Items.SNOWBALL)>0),"Killer gives everyone the killer role and knife");
        check(entities(s,"@a[tag=queued,team=ingame_players,scores={bb_team=0}]")==4,"Killer has no red/blue assignments and uses the combat team with friendly fire");
        cmd(s,"function mcm:game/loops/ingame");
        check(score(s,"$gamestate","CmdData")==1,"full Killer loop bypasses Classic no-innocent victory");
        var killers=List.copyOf(s.getPlayerList().getPlayers());
        var killer=killers.get(0); var victim=killers.get(1);
        hit(s,killer,killer);
        check(!killer.getTags().contains("spectating") && adrenalineDrops(s)==0,"Killer self-hit gives no kill or reward");
        killers.get(3).removeTag("queued");
        hit(s,killers.get(3),victim);
        check(!victim.getTags().contains("spectating") && adrenalineDrops(s)==0,"unqueued attacker cannot kill or earn adrenaline");
        killers.get(3).addTag("queued");
        cmd(s,"scoreboard players set $kill_reward GameRules 3");
        int scrap=killer.getInventory().countItem(Items.NETHERITE_SCRAP);
        killer.addTag("HoldKnife");
        victim.invulnerableTime=0;
        cmd(s,"damage " + victim.getScoreboardName() + " 1 minecraft:player_attack by " + killer.getScoreboardName());
        killer.removeTag("HoldKnife");
        check(victim.getTags().contains("spectating"),"real melee damage kills another Killer without team immunity");
        check(killer.getInventory().countItem(Items.NETHERITE_SCRAP)==scrap+3,"Killer kill preserves the configured fixed scrap reward");
        check(adrenalineDrops(s)==1,"one weapon kill drops exactly one extra adrenaline bottle");
        call(s,victim,"mcm:game/player_hit");
        check(adrenalineDrops(s)==1 && killer.getInventory().countItem(Items.NETHERITE_SCRAP)==scrap+3,"repeated hit on an eliminated player cannot duplicate either reward");
        cmd(s,"scoreboard players set $valid_drop temp 0");
        cmd(s,"execute as @e[type=item,tag=bb_kill_adrenaline] if items entity @s contents carrot_on_a_stick[item_model=\"minecraft:role_items/adrenaline\",custom_data~{adrenaline:1b,item:\"adrenaline\"}] run scoreboard players add $valid_drop temp 1");
        check(score(s,"$valid_drop","temp")==1,"dropped adrenaline has the loadout bottle's model and usable item data");
        cmd(s,"execute at " + victim.getScoreboardName() + " store result score $nearby_drop temp if entity @e[type=item,tag=bb_kill_adrenaline,distance=..1]");
        check(score(s,"$nearby_drop","temp")==1,"bonus bottle drops at the victim's position");
        cmd(s,"function mcm:modes/tick");
        check(score(s,"$killer_alive","CmdData")==3 && score(s,"$gamestate","CmdData")==1,"Killer continues with three individual survivors");
        check(score(s,victim.getScoreboardName(),"bb_respawn")==0,"eliminated Killer never schedules a respawn");
        cmd(s,"bossbar add gamedisplay \"Test\"");
        cmd(s,"function mcm:game/loops/updatebossbar");
        var killerBar=s.getCustomBossEvents().get(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("minecraft","gamedisplay"));
        check(killerBar.getName().getString().equals("Players left: 3") && killerBar.getValue()==3 && killerBar.getMax()==4,"Killer bossbar shows individual survivors without a countdown");
        cmd(s,"scoreboard players set $kill_reward GameRules 0");
        hit(s,killer,killers.get(2));
        check(adrenalineDrops(s)==2 && killer.getInventory().countItem(Items.NETHERITE_SCRAP)==scrap+3,"zero scrap per kill still drops one adrenaline bottle");
        hit(s,victim,killers.get(3));
        check(!killers.get(3).getTags().contains("spectating") && adrenalineDrops(s)==2,"spectating attacker cannot kill or drop adrenaline");
        cmd(s,"function mcm:modes/tick");
        check(score(s,"$gamestate","CmdData")==1 && score(s,"$killer_alive","CmdData")==2,"two surviving Killers remain opponents");
        cmd(s,"scoreboard players set $kill_reward GameRules -1");
        cmd(s,"give " + killers.get(3).getScoreboardName() + " netherite_scrap 7");
        hit(s,killer,killers.get(3));
        check(adrenalineDrops(s)==3 && killer.getInventory().countItem(Items.NETHERITE_SCRAP)==scrap+10,"take-victim-scrap option transfers all seven scraps alongside adrenaline");
        cmd(s,"function mcm:modes/tick");
        check(score(s,"$gamestate","CmdData")==2 && killer.getTags().contains("bb_killer_winner"),"last individual Killer wins");
        cmd(s,"scoreboard players set $gameEndTimer CmdData 200");
        cmd(s,"function mcm:game/loops/gameend");
        check(entities(s,"@a[tag=WonLast]")==1 && killer.getTags().contains("WonLast"),"Killer result awards victory only to the last survivor");
        start(s,2);
        check(entities(s,"@a[tag=bb_killer_winner]")==0,"next round clears the previous individual winner");
        victim=killers.get(1);
        victim.setLastHurtByMob(killer);
        call(s,victim,"mcm:game/playerdeath");
        check(adrenalineDrops(s)==0 && killer.getInventory().countItem(Items.NETHERITE_SCRAP)==0,"hazard death with a stale attacker awards neither adrenaline nor scrap");
        start(s,2);
        victim.setClientLoaded(true);
        victim.invulnerableTime=0;
        cmd(s,"summon arrow 0 2 70 {Tags:[\"knife\",\"bb_test_knife\"]}");
        cmd(s,"damage " + victim.getScoreboardName() + " 1 minecraft:arrow by @e[type=arrow,tag=bb_test_knife,limit=1] from " + killer.getScoreboardName());
        cmd(s,"kill @e[tag=bb_test_knife]");
        check(victim.getTags().contains("spectating") && adrenalineDrops(s)==1,"real thrown-knife damage kills another Killer and drops one bottle");
        var bottle=s.overworld().getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,victim.getBoundingBox().inflate(1)).stream().filter(e->e.getTags().contains("bb_kill_adrenaline")).findFirst().orElseThrow();
        int sticks=killer.getInventory().countItem(Items.CARROT_ON_A_STICK);
        bottle.setNoPickUpDelay();
        bottle.playerTouch(killer);
        check(bottle.isRemoved() && killer.getInventory().countItem(Items.CARROT_ON_A_STICK)==sticks+1,"kill-drop adrenaline can be picked up as an additional bottle");
        start(s,2);
        cmd(s,"execute as @a run function mcm:game/playerdeath");
        cmd(s,"function mcm:modes/tick");
        check(score(s,"$gamestate","CmdData")==2 && score(s,"$killer_alive","CmdData")==0 && score(s,"$winner","CmdData")==0,"simultaneous elimination of every Killer draws");
        start(s,2);
        cmd(s,"scoreboard players set $gametimer CmdData 1");
        cmd(s,"function mcm:game/loops/game_timer");
        cmd(s,"function mcm:modes/tick");
        check(score(s,"$gamestate","CmdData")==1 && score(s,"$winner","CmdData")==0 && score(s,"$innocentWin","CmdData")==0,"Killer keeps playing when the configured timer reaches zero");
        for(int i=0;i<3;i++) cmd(s,"function mcm:game/loops/ingame");
        check(score(s,"$gamestate","CmdData")==1 && score(s,"$killer_alive","CmdData")==4 && score(s,"$gametimer","CmdData")==-3,"full Killer loop continues beyond the time limit with all survivors");
        for(int i=1;i<4;i++) hit(s,killer,killers.get(i));
        cmd(s,"function mcm:modes/tick");
        check(score(s,"$gamestate","CmdData")==2 && killer.getTags().contains("bb_killer_winner"),"last standing Killer wins after the configured time limit has passed");
        start(s,2);
        cmd(s,"tp " + killer.getScoreboardName() + " 100 10 100");
        cmd(s,"tp " + killers.get(1).getScoreboardName() + " 110 10 100");
        cmd(s,"tp " + killers.get(2).getScoreboardName() + " 140 10 100");
        cmd(s,"tp " + killers.get(3).getScoreboardName() + " 160 10 100");
        call(s,killer,"mcm:modes/tracker");
        check(score(s,"$out","temp")==10,"Killer tracker finds the nearest opponent and excludes its user");
        call(s,killers.get(1),"mcm:game/playerdeath");
        call(s,killer,"mcm:modes/tracker");
        check(score(s,"$out","temp")==40,"Killer tracker excludes eliminated players");
        cmd(s,"tag @e[type=marker,tag=PlayerSpawn] remove PlayerSpawn");
        for(int i=0;i<4;i++) cmd(s,"summon marker " + (i*10) + " 2 70 {Tags:[\"PlayerSpawn\"]}");
        check(entities(s,"@e[type=marker,tag=PlayerSpawn]")==4,"teleporter fixture has four loaded player spawns");
        call(s,killer,"mcm:game/items/murderer/teleporter");
        check(killer.getX()==100.5 && killers.get(1).getX()==110.5 && killers.get(2).getX()>=.5 && killers.get(2).getX()<=30.5 && killers.get(3).getX()>=.5 && killers.get(3).getX()<=30.5,"Killer teleporter moves every live opponent and leaves user and spectators in place");
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
