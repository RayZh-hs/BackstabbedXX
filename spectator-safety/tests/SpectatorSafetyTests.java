package gravity_changer.test;
import java.util.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.level.GameType;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;
@PrefixGameTestTemplate(false)
public final class SpectatorSafetyTests {
    @GameTest(template="empty",templateNamespace="gravity_changer",batch="spectator_safety",timeoutTicks=100)
    public static void knifeOwner(GameTestHelper h) {
        var online=players(h);var p=player(h,"KnifeOwner");online.add(p);
        try {
            p.addTag("queued");p.addTag("murderer");p.setPos(10,4,0);
            cmd(p,"scoreboard objectives add playerUUID dummy");cmd(p,"scoreboard objectives add dead dummy");cmd(p,"scoreboard players reset @s dead");
            cmd(p,"execute store result score @s playerUUID run data get entity @s UUID[0]");
            cmd(p,"summon item 0 4 0 {Tags:[\"spectator_test_knife\",\"knifeCosmetic\"],Item:{id:\"minecraft:snowball\",count:1}}");
            cmd(p,"data modify entity @e[tag=spectator_test_knife,limit=1] Owner set from entity @s UUID");
            var item=h.getLevel().getEntities(net.minecraft.world.entity.EntityType.ITEM,e->e.getTags().contains("spectator_test_knife")).getFirst();
            Vec3 start=item.position();
            p.setGameMode(GameType.SPECTATOR);
            cmd(p,"execute as @e[tag=spectator_test_knife] at @s run function mcm:game/items/knife/stuck");
            h.assertTrue(item.position().equals(start),"Spectator owner must not attract the knife");
            p.setGameMode(GameType.ADVENTURE);p.addTag("spectating");
            cmd(p,"execute as @e[tag=spectator_test_knife] at @s run function mcm:game/items/knife/stuck");
            h.assertTrue(item.position().equals(start),"Tagged spectator must not attract the knife");
            p.removeTag("spectating");cmd(p,"scoreboard players set @s dead 1");
            cmd(p,"execute as @e[tag=spectator_test_knife] at @s run function mcm:game/items/knife/stuck");
            h.assertTrue(item.position().equals(start),"Eliminated owner must not attract the knife");
            cmd(p,"scoreboard players reset @s dead");
            cmd(p,"execute as @e[tag=spectator_test_knife] at @s run function mcm:game/items/knife/stuck");
            h.assertTrue(!item.position().equals(start),"Living owner still unsticks their knife with an unset death score");
            var id=p.getUUID();int a=(int)(id.getMostSignificantBits()>>32),b=(int)id.getMostSignificantBits(),c=(int)(id.getLeastSignificantBits()>>32),d=(int)id.getLeastSignificantBits();
            cmd(p,"data modify entity @e[tag=spectator_test_knife,limit=1] Owner set value [I;"+a+","+b+","+c+","+(d^1)+"]");
            start=item.position();cmd(p,"execute as @e[tag=spectator_test_knife] at @s run function mcm:game/items/knife/stuck");
            h.assertTrue(item.position().equals(start),"A UUID prefix collision must not attract somebody else's knife");
            System.out.println("SPECTATOR SAFETY PASS: knife spectator/tag/death/live/full UUID");
        } finally {cmd(p,"kill @e[tag=spectator_test_knife]");online.remove(p);p.discard();}h.succeed();
    }
    @GameTest(template="empty",templateNamespace="gravity_changer",batch="spectator_safety",timeoutTicks=100)
    public static void trackerTargets(GameTestHelper h) {
        var online=players(h);var ps=new ArrayList<ServerPlayer>();
        try {
            for(int i=0;i<3;i++){var p=player(h,"Track"+i);online.add(p);ps.add(p);p.addTag("queued");p.addTag("murderer");p.setPos(i==0?0:i==1?3:10,10,0);}
            var source=ps.getFirst();var ghost=ps.get(1);
            cmd(source,"scoreboard objectives add temp dummy");cmd(source,"scoreboard objectives add dead dummy");cmd(source,"scoreboard players reset @a dead");
            ghost.setGameMode(GameType.SPECTATOR);
            cmd(source,"function mcm:modes/tracker");
            h.assertTrue(value(source,"$out","temp")==10,"Tracker must skip native spectator without a spectating tag");
            ghost.setGameMode(GameType.ADVENTURE);cmd(ghost,"scoreboard players set @s dead 1");
            cmd(source,"function mcm:modes/tracker");h.assertTrue(value(source,"$out","temp")==10,"Tracker must skip eliminated target");
            cmd(ghost,"scoreboard players reset @s dead");cmd(source,"function mcm:modes/tracker");h.assertTrue(value(source,"$out","temp")==3,"Tracker selects living nearest target");
            ghost.addTag("spectating");ps.get(2).setGameMode(GameType.SPECTATOR);cmd(source,"scoreboard players set $out temp -99");cmd(source,"function mcm:modes/tracker");
            h.assertTrue(value(source,"$out","temp")==-99,"No target must not calculate a self-distance");
            h.assertTrue(!source.getTags().contains("bb_tracking"),"Temporary self-exclusion tag is cleaned");
            for(var p:ps)p.addTag("innocent");source.removeTag("innocent");
            ghost.removeTag("spectating");ghost.setGameMode(GameType.SPECTATOR);ps.get(2).setGameMode(GameType.ADVENTURE);
            cmd(source,"function mcm:game/items/player_tracker/track");h.assertTrue(value(source,"$out","temp")==10,"Classic tracker also skips native spectators");
            source.setGameMode(GameType.SPECTATOR);cmd(source,"scoreboard players set $out temp -99");cmd(source,"function mcm:game/items/player_tracker/track");
            h.assertTrue(value(source,"$out","temp")==-99,"Spectating tracker user cannot calculate a target");
            System.out.println("SPECTATOR SAFETY PASS: tracker classic/killer/spectator/death/live/no target");
        } finally {for(var p:ps){online.remove(p);p.discard();}}h.succeed();
    }
    @GameTest(template="empty",templateNamespace="gravity_changer",batch="spectator_safety",timeoutTicks=100)
    public static void noSpectatorRecovery(GameTestHelper h) {
        var online=players(h);var p=player(h,"GhostRecall");online.add(p);
        try {
            p.addTag("queued");p.addTag("murderer");p.addTag("free_knife");
            for(String obj:List.of("dead","GameRules","mcm_missing","mcm_epoch","temp"))cmd(p,"scoreboard objectives add "+obj+" dummy");
            cmd(p,"scoreboard players set $knife_timeout GameRules 1");cmd(p,"scoreboard players set $knife_ticks GameRules 1000");
            cmd(p,"scoreboard players set @s mcm_missing 99");cmd(p,"scoreboard players set @s mcm_epoch 0");cmd(p,"scoreboard players reset @s dead");
            for(int state=0;state<3;state++){
                p.setGameMode(state==0?GameType.SPECTATOR:GameType.ADVENTURE);
                if(state==1)p.addTag("spectating");else p.removeTag("spectating");
                if(state==2)cmd(p,"scoreboard players set @s dead 1");
                cmd(p,"function mcm:extensions/knife/tick");cmd(p,"function mcm:extensions/knife/recover");
                cmd(p,"function mcm:game/items/knife_retrieve {retrieve:knife,cost:2}");
                h.assertTrue(score(p,"mcm_missing")==99 && score(p,"mcm_epoch")==0 && p.getTags().contains("free_knife"),"Inactive player must not count down, recover or consume recall");
            }
            cmd(p,"scoreboard players reset @s dead");cmd(p,"function mcm:extensions/knife/tick");
            h.assertTrue(score(p,"mcm_missing")==100,"Living owner timeout still advances");
            System.out.println("SPECTATOR SAFETY PASS: timeout and explicit recall guard");
        } finally {cmd(p,"scoreboard players set $knife_timeout GameRules 0");online.remove(p);p.discard();}h.succeed();
    }
    private static int value(ServerPlayer p,String who,String obj){var s=p.getServer().getScoreboard();var v=s.getPlayerScoreInfo(net.minecraft.world.scores.ScoreHolder.forNameOnly(who),s.getObjective(obj));return v==null?0:v.value();}
    private static int score(ServerPlayer p,String name){var s=p.getServer().getScoreboard();return s.getOrCreatePlayerScore(p,s.getObjective(name)).get();}
    private static void cmd(ServerPlayer p,String text){p.getServer().getCommands().performPrefixedCommand(p.getServer().createCommandSourceStack().withEntity(p).withPosition(p.position()).withLevel(p.serverLevel()).withPermission(4).withSuppressedOutput(),text);}
    private static ServerPlayer player(GameTestHelper h,String name){
        var profile=new com.mojang.authlib.GameProfile(UUID.randomUUID(),name);
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),profile,net.minecraft.server.level.ClientInformation.createDefault());
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p,net.minecraft.server.network.CommonListenerCookie.createInitial(profile,false)){
            @Override public boolean hasChannel(net.minecraft.resources.ResourceLocation channel){return false;}
            @Override public void send(net.minecraft.network.protocol.Packet<?> packet){}
            @Override public void send(net.minecraft.network.protocol.Packet<?> packet,net.minecraft.network.PacketSendListener listener){}
        };p.setClientLoaded(true);p.initInventoryMenu();h.getLevel().addNewPlayer(p);return p;
    }
    @SuppressWarnings("unchecked")private static List<ServerPlayer> players(GameTestHelper h){try{var f=net.minecraft.server.players.PlayerList.class.getDeclaredField("players");f.setAccessible(true);return(List<ServerPlayer>)f.get(h.getLevel().getServer().getPlayerList());}catch(Exception e){throw new RuntimeException(e);}}
}
