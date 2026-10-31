package gravity_changer.test;

import java.util.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.level.GameType;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

@PrefixGameTestTemplate(false)
public final class LobbyBoundaryTests {
    @GameTest(template="empty",templateNamespace="gravity_changer",batch="lobby_boundary",timeoutTicks=400)
    public static void lobbyWaitAndNormalEntry(GameTestHelper h) {
        if(!Boolean.getBoolean("backstabbed.lobbyGate")){h.succeed();return;}
        List<ServerPlayer> ps=new ArrayList<>(),online=players(h);
        try {
            for(int i=0;i<6;i++){var p=player(h,"Gate"+i);ps.add(p);online.add(p);if(i<4)p.addTag("queued");}
            var source=ps.getFirst();ps.get(5).addTag("queued");ps.get(5).setGameMode(GameType.SPECTATOR);
            for(String obj:List.of("CmdData","dead","test_deaths","kb_cd"))cmd(source,"scoreboard objectives add "+obj+" dummy");
            String[] arenas={"underwater_base","klut27","middle_ages"};int[] ids={19,20,22};
            List<String> premature=new ArrayList<>();
            for(int k=0;k<arenas.length;k++){
                cmd(source,"scoreboard players set $selectedMap CmdData "+ids[k]);
                cmd(source,"scoreboard players set $gamestate CmdData 0");
                for(int countdown:new int[]{199,100,2}){
                    for(int i=0;i<ps.size();i++){ps.get(i).setPos(-25+i,-2,93);cmd(ps.get(i),"scoreboard players set @s dead 0");}
                    cmd(source,"scoreboard players set $startcountdown CmdData "+countdown);
                    cmd(source,"function bbe_arena:"+arenas[k]+"/tick");
                    for(int i=0;i<ps.size();i++)if(ps.get(i).position().distanceToSqr(new Vec3(-25+i,-2,93))>1e-8){premature.add(arenas[k]+" countdown="+countdown+" player="+i);break;}
                }
            }
            h.assertTrue(premature.isEmpty(),"Queued lobby players moved before start: "+premature);
            for(int k=0;k<arenas.length;k++){
                String arena=arenas[k];
                cmd(source,"scoreboard players set $selectedMap CmdData "+ids[k]);
                cmd(source,"scoreboard players set $gamestate CmdData 2");
                cmd(source,"function bbe_arena:"+arena+"/tick");
                h.assertTrue(source.getX()==-25,"Game end does not enforce active boundary");
                cmd(source,"scoreboard players set $gamestate CmdData 1");
                cmd(source,"scoreboard players set $selectedMap CmdData 999");
                cmd(source,"function bbe_arena:"+arena+"/tick");
                h.assertTrue(source.getX()==-25,"Unselected arena cannot move players");
                // The real start function must distribute participants to unoccupied spawns.
                ps.get(5).removeTag("queued");
                cmd(source,"scoreboard players set $selectedMap CmdData "+ids[k]);
                cmd(source,"scoreboard players set $gamestate CmdData 0");
                cmd(source,"kill @e[type=marker,tag=PlayerSpawn]");
                h.getLevel().getChunk(0,0);h.getLevel().getChunk(1,0);
                for(int i=0;i<4;i++)cmd(source,"summon marker "+(10+3*i)+" 20 10 {Tags:[\"PlayerSpawn\",\"LobbyTestSpawn\"]}");
                cmd(source,"function mcm:maps/start");
                Set<Vec3> destinations=new HashSet<>();
                for(int i=0;i<4;i++){var p=ps.get(i);destinations.add(p.position());h.assertTrue(p.getY()==20&&p.getZ()==10.5&&Set.of(10.5,13.5,16.5,19.5).contains(p.getX()),"Normal map start uses spawn markers: "+p.position());}
                h.assertTrue(destinations.size()==4,"Normal map start allocates four different spawns");
                ps.get(5).addTag("queued");
                cmd(source,"function bbe_arena:"+arena+"/tp");
                Vec3 fallback=source.position();
                h.getLevel().getChunk(source.blockPosition());
                String runtime=new String[]{"UnderwaterBaseRuntime","Klut27Runtime","MiddleAgesRuntime"}[k];
                Vec3 near=fallback.add(1,0,0),closer=fallback.add(2,0,0),outside=fallback.add(1000,0,0);
                // Two valid markers, a wrong-map marker, and an out-of-bounds marker.
                for(int offset:new int[]{1,2,3,999}){
                    Vec3 pos=fallback.add(offset,0,0);
                    h.getLevel().getChunk(net.minecraft.core.BlockPos.containing(pos));
                    cmd(source,"summon marker "+pos.x+" "+pos.y+" "+pos.z+" {Tags:[\"PlayerSpawn\",\"YachtGateSpawn\",\""+(offset==3?"WrongArenaRuntime":runtime)+"\"]}");
                }
                // A test-only recorder replaces the downstream elimination function;
                // the installed boundary predicates/check/kill functions remain real.
                for(var p:ps){p.setPos(-25,-2,93);cmd(p,"scoreboard players set @s dead 0");cmd(p,"scoreboard players set @s test_deaths 0");}
                for(int grace:new int[]{300,1,0}){
                    cmd(source,"scoreboard players set $graceperiod CmdData "+grace);
                    for(int i=0;i<4;i++){ps.get(i).setPos(outside);cmd(ps.get(i),"scoreboard players set @s dead 0");cmd(ps.get(i),"scoreboard players set @s test_deaths 0");}
                    cmd(source,"function bbe_arena:"+arena+"/tick");
                    for(int i=0;i<4;i++){
                        h.assertTrue(score(ps.get(i),"test_deaths")== (grace>0?0:1),"Preparation rescues, exact grace expiry eliminates: "+arena+" grace="+grace);
                        if(grace>0)h.assertTrue(ps.get(i).position().distanceToSqr(closer)<1e-8,"Nearest valid current-arena spawn selected; invalid markers excluded: "+ps.get(i).position()+" expected "+closer);
                    }
                    h.assertTrue(score(ps.get(4),"test_deaths")==0&&score(ps.get(5),"test_deaths")==0,"Nonparticipants and spectators remain excluded");
                }
                cmd(source,"kill @e[type=marker,tag=YachtGateSpawn]");
                cmd(source,"scoreboard players set $graceperiod CmdData 1");
                for(int i=0;i<4;i++){ps.get(i).setPos(outside);cmd(ps.get(i),"scoreboard players set @s dead 0");cmd(ps.get(i),"scoreboard players set @s test_deaths 0");}
                if(arena.equals("klut27")){
                    source.addTag("KlutBootsEquipped");source.addTag("KlutBootsUp");
                    cmd(source,"gravity set_base_direction up @s");gravity_changer.api.GravityChangerAPI.getGravityComponent(source).tick();source.setPos(outside);
                    cmd(source,"effect give @s jump_boost infinite 2 true");cmd(source,"effect give @s slow_falling infinite 0 true");cmd(source,"scoreboard players set @s kb_cd 150");
                }
                cmd(source,"function bbe_arena:"+arena+"/tick");
                h.assertTrue(source.position().distanceToSqr(fallback)<1e-8&&score(source,"test_deaths")==0,"Missing-marker fallback remains safe during preparation");
                if(arena.equals("klut27")){
                    h.assertTrue(gravity_changer.api.GravityChangerAPI.getGravityDirection(source)==net.minecraft.core.Direction.DOWN&&!source.hasEffect(net.minecraft.world.effect.MobEffects.JUMP)&&!source.hasEffect(net.minecraft.world.effect.MobEffects.SLOW_FALLING)&&score(source,"kb_cd")==150,"Inverted boots rescue clears attached effects and preserves cooldown");
                    source.setPos(outside);cmd(source,"function klut27:fall");
                    h.assertTrue(source.position().distanceToSqr(fallback)<1e-8&&score(source,"test_deaths")==0,"KLUT legacy boundary path also rescues during grace");
                    cmd(source,"scoreboard players set $graceperiod CmdData 0");source.setPos(outside);cmd(source,"function klut27:fall");
                    h.assertTrue(score(source,"test_deaths")==1,"KLUT legacy path eliminates after grace");
                }
                for(int i=0;i<4;i++){var p=ps.get(i);cmd(p,"function bbe_arena:"+arena+"/tp");cmd(p,"scoreboard players set @s dead 0");cmd(p,"scoreboard players set @s test_deaths 0");}
                cmd(source,"function bbe_arena:"+arena+"/tick");
                for(int i=0;i<4;i++)h.assertTrue(score(ps.get(i),"test_deaths")==0,"In-bounds players remain safe");
                for(int i=0;i<ps.size();i++)ps.get(i).setPos(-25+i,-2,93);
                System.out.println("YACHT POLICY PASSED: "+arena+"; lobby/end/unselected, normal start, grace rescue/expiry death, nearest marker/fallback, spectator scope");
            }
        } finally {for(var p:ps){online.remove(p);p.discard();}}
        h.succeed();
    }
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
