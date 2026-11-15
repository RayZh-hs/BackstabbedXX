package gravity_changer.test;

import java.util.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.*;
import net.minecraft.world.entity.*;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

@net.neoforged.fml.common.EventBusSubscriber(modid="gravity_changer",bus=net.neoforged.fml.common.EventBusSubscriber.Bus.MOD)
@PrefixGameTestTemplate(false)
public final class LobbyVotingTests {
    private static final String V="mcm:lobby/voting/";
    @net.neoforged.bus.api.SubscribeEvent public static void register(net.neoforged.neoforge.event.RegisterGameTestsEvent e) {e.register(LobbyVotingTests.class);}
    @GameTest(template="empty",templateNamespace="gravity_changer",batch="voting_eight",timeoutTicks=400)
    public static void eightCandidatesAndFairTies(GameTestHelper h) {
        var level=h.getLevel();var forced=new ArrayList<net.minecraft.world.level.ChunkPos>();
        for(int x=0;x<=2;x++) for(int z=5;z<=8;z++) {
            var pos=new net.minecraft.world.level.ChunkPos(x,z);
            if(!level.getForcedChunks().contains(pos.toLong())) {level.setChunkForced(x,z,true);forced.add(pos);}
            level.getChunk(x,z);
        }
        h.runAfterDelay(10,()->{
            try {
                var f=ServerLevel.class.getDeclaredField("entityManager");f.setAccessible(true);
                @SuppressWarnings("unchecked") var m=(net.minecraft.world.level.entity.PersistentEntitySectionManager<Entity>)f.get(level);
                for(int x=0;x<=2;x++)for(int z=5;z<=8;z++)m.updateChunkStatus(new net.minecraft.world.level.ChunkPos(x,z),net.minecraft.world.level.entity.Visibility.TICKING);
            }catch(ReflectiveOperationException e){throw new RuntimeException(e);}
            var p=player(h,"VoteAlice");var q=player(h,"VoteBob");var online=players(h);online.add(p);online.add(q);
            p.setPos(25,1,121);q.setPos(25,1,126);
            try {
                for(String o:List.of("CmdData","GameRules","temp","math","vote_position","vote_map_id","vote_count","MapValues","mapvote","current_vote","gameID"))command(p,"scoreboard objectives add "+o+" dummy");
                command(p,"scoreboard players set $two math 2");
                command(p,"scoreboard players set $gamestate CmdData -1");
                command(p,"data remove storage mcm:options init");
                command(p,"data remove storage mcm:options options.locked");
                command(p,"data modify storage mcm:options options.map_toggle set value {maps:[],page:0,page_size:9,max_page:1}");
                command(p,"kill @e[type=marker,tag=MapVote]");
                for(int i=1;i<=10;i++) {
                    command(p,"summon marker 24 6 100 {Tags:[\"MapVote\",\"VotingFixture\",\"VotingMap"+i+"\"]}");
                    command(p,"scoreboard players set @e[type=marker,tag=VotingMap"+i+"] MapValues "+i);
                    command(p,"data modify storage mcm:options options.map_toggle.maps append value \"VotingMap"+i+"\"");
                    enabled(p,i,true);
                }
                command(p,"summon marker 24 6 100 {Tags:[\"MapVote\",\"Random\",\"VotingFixture\"]}");
                command(p,"scoreboard players set @e[type=marker,tag=Random] MapValues -1");
                command(p,"function "+V+"start");
                h.assertTrue(slots(h).size()==9,"Eight concrete slots and one random slot");
                h.assertTrue(ids(h).size()==8,"Eight distinct candidates from ten enabled maps");
                h.assertTrue(level.getEntities(EntityType.ITEM_DISPLAY,e->e.getTags().contains("vote_display")).size()==9,"All nine posters are visible");
                for(var poster:level.getEntities(EntityType.ITEM_DISPLAY,e->e.getTags().contains("vote_display"))) {
                    boolean random=poster.getZ()<86;
                    double expectedX=random?27.99:28.99;
                    h.assertTrue(Math.abs(poster.getX()-expectedX)<0.00001,"Legacy poster model plane must sit 0.01 blocks in front of wall, anchor x="+poster.getX());
                    h.assertTrue(Math.abs(poster.getZ()-Math.rint(poster.getZ()))<0.00001,"Poster Z must not gain the implicit half-block offset");
                }
                h.assertTrue(level.getEntities(EntityType.INTERACTION,e->e.getTags().contains("VoteReroll")).size()==1,"One physical reroll control");
                var reroll=level.getEntities(EntityType.INTERACTION,e->e.getTags().contains("VoteReroll")).getFirst();
                h.assertTrue(Math.abs(reroll.getX()-26.87)<0.00001 && Math.abs(reroll.getZ()-80.5)<0.00001,"Reroll belongs on the wall left of Random");
                command(p,"function "+V+"vote_slots/map7");command(q,"function "+V+"vote_slots/map8");
                h.assertTrue(score(p,"map7","vote_count")==1 && score(p,"map8","vote_count")==1,"New slots receive votes");
                command(p,"function "+V+"vote_slots/map8");
                h.assertTrue(score(p,"map7","vote_count")==0 && score(p,"map8","vote_count")==2,"Changing vote moves exactly one ballot");
                command(p,"function "+V+"vote_slots/map8");
                h.assertTrue(score(p,"map8","vote_count")==2,"Repeated vote never duplicates");

                int id7=entityScore(slot(h,7),"vote_map_id"),id8=entityScore(slot(h,8),"vote_map_id"),id1=entityScore(slot(h,1),"vote_map_id");
                scores(p,0);command(p,"scoreboard players set map7 vote_count 3");command(p,"scoreboard players set map8 vote_count 3");
                draws(h,p,Set.of(id7,id8),128,"Concrete tie");
                command(p,"scoreboard players set random vote_count 3");
                draws(h,p,Set.of(id7,id8),128,"Random tied never admits low-vote maps");
                command(p,"scoreboard players set map1 vote_count 3");
                draws(h,p,Set.of(id1,id7,id8),160,"Three concrete leaders plus random tie");
                command(p,"scoreboard players set random vote_count 4");
                draws(h,p,ids(h),256,"Random alone ahead reaches every displayed candidate");
                scores(p,0);command(p,"scoreboard players set map8 vote_count 5");
                draws(h,p,Set.of(id8),8,"Unique highest vote");

                command(p,"scoreboard players set $countdown CmdData 4");
                command(p,"function "+V+"reroll");
                h.assertTrue(!p.getTags().contains("Voted") && score(p,"map8","vote_count")==0 && score(p,"$countdown","CmdData")==20,"Reroll clears ballots and restarts countdown");
                h.assertTrue(score(p,"$countSec","CmdData")==0,"Fresh countdown has a full first second");
                for(int i=2;i<=10;i++) enabled(p,i,false);
                command(p,"function "+V+"enabled_changed");
                h.assertTrue(ids(h).equals(Set.of(1)),"Only enabled candidates remain after immediate refresh");
                h.assertTrue(slots(h).stream().filter(e->e.getTags().contains("disabled")).count()==7,"Empty slots disabled");
                scores(p,0);command(p,"scoreboard players set map8 vote_count 999");command(p,"scoreboard players set random vote_count 1");
                draws(h,p,Set.of(1),8,"Disabled slot cannot win even with stale high count");
                // Exercise the actual options callback, not just a direct refresh helper.
                command(p,"function mcm:lobby/options/map_toggle/map_slot_interaction_inner {map:VotingMap2}");
                h.assertTrue(ids(h).equals(Set.of(1,2)),"Changing enabled map immediately rebuilds candidates");
                command(p,"function "+V+"vote_slots/map1");
                var beforePage=slots(h).stream().map(Entity::getUUID).collect(java.util.stream.Collectors.toSet());
                command(p,"function mcm:lobby/options/map_toggle/page_interaction {diff:1}");
                h.assertTrue(p.getTags().contains("Voted") && beforePage.equals(slots(h).stream().map(Entity::getUUID).collect(java.util.stream.Collectors.toSet())),"Pagination preserves ballots and candidate entities");
                command(p,"execute store result score $test_page temp run data get storage mcm:options options.map_toggle.page");
                h.assertTrue(score(p,"$test_page","temp")==1,"Pagination really changed the page");
                // Empty pool must keep voting open, with random disabled too.
                enabled(p,1,false);enabled(p,2,false);command(p,"function "+V+"enabled_changed");
                h.assertTrue(ids(h).isEmpty() && slots(h).stream().allMatch(e->e.getTags().contains("disabled")),"No maps disables every slot");
                command(p,"function "+V+"end");
                h.assertTrue(score(p,"$gamestate","CmdData")==-1 && !hasScore(p,"$selectedMap","CmdData"),"Empty pool cannot activate a stale map");
                enabled(p,1,true);command(p,"function "+V+"enabled_changed");
                command(p,"function "+V+"vote_slots/map1");
                command(p,"data modify storage mcm:options options.locked set value 1");
                command(p,"function "+V+"reroll");
                h.assertTrue(p.getTags().contains("Voted"),"Locked manual reroll cannot clear votes");
                command(p,"data remove storage mcm:options options.locked");
                command(p,"scoreboard players set $gamestate CmdData 1");
                command(p,"function "+V+"reroll");command(p,"function "+V+"enabled_changed");
                h.assertTrue(p.getTags().contains("Voted") && score(p,"$gamestate","CmdData")==1,"Game guards preserve running round");
                command(p,"scoreboard players set $gamestate CmdData 0");
                // Use no selected arena in the isolated fixture; cancellation still traverses the real path.
                command(p,"scoreboard players reset $selectedMap CmdData");
                command(p,"scoreboard players set $start CmdData 1");
                command(p,"schedule function klut27:activate 1s replace");
                command(p,"function "+V+"reroll");
                h.assertTrue(score(p,"$gamestate","CmdData")==-1 && score(p,"$start","CmdData")==0,"Preparation reroll returns to voting and stops countdown");
                command(p,"execute store success score $pending_activation temp run schedule clear klut27:activate");
                h.assertTrue(score(p,"$pending_activation","temp")==0,"Old delayed map activation is already cancelled");
                command(p,"function "+V+"set_maps");command(p,"function "+V+"set_maps");
                h.assertTrue(slots(h).size()==9 && level.getEntities(EntityType.INTERACTION,e->e.getTags().contains("VoteReroll")).size()==1,"Repeated rebuild is idempotent");
                System.out.println("VOTING_EIGHT_PASS slots, ballots, all tie pools, 688 random draws, enabled edits, empty pool, locks, preparation and rebuild");
            } finally {
                command(p,"kill @e[tag=VotingFixture]");command(p,"kill @e[tag=MapVoteEntity]");command(p,"kill @e[tag=vote_display]");
                command(p,"execute as @e[tag=VoteReroll] on passengers run kill @s");command(p,"kill @e[tag=VoteReroll]");
                command(p,"scoreboard players set $gamestate CmdData 0");command(p,"scoreboard players reset $selectedMap CmdData");
                online.remove(p);online.remove(q);p.discard();q.discard();
                for(var pos:forced)level.setChunkForced(pos.x,pos.z,false);
            }
            h.succeed();
        });
    }
    private static void enabled(Entity p,int i,boolean enabled){command(p,"data modify storage mcm:options options.map_toggle.VotingMap"+i+".enabled set value "+(enabled?1:0));}
    private static void scores(Entity p,int n){for(String k:List.of("random","map1","map2","map3","map4","map5","map6","map7","map8"))command(p,"scoreboard players set "+k+" vote_count "+n);}
    private static List<? extends Interaction> slots(GameTestHelper h){return h.getLevel().getEntities(EntityType.INTERACTION,e->e.getTags().contains("vote_counter"));}
    private static Interaction slot(GameTestHelper h,int n){return slots(h).stream().filter(e->e.getTags().contains("map"+n)).findFirst().orElseThrow();}
    private static Set<Integer> ids(GameTestHelper h){var result=new HashSet<Integer>();for(var e:slots(h))if(!e.getTags().contains("disabled") && !e.getTags().contains("map_random"))result.add(entityScore(e,"vote_map_id"));return result;}
    private static int entityScore(Entity e,String o){return score(e,e.getScoreboardName(),o);}
    private static int score(Entity e,String name,String o){var b=e.getServer().getScoreboard();return b.getOrCreatePlayerScore(net.minecraft.world.scores.ScoreHolder.forNameOnly(name),b.getObjective(o)).get();}
    private static boolean hasScore(Entity e,String name,String o){var b=e.getServer().getScoreboard();return b.getPlayerScoreInfo(net.minecraft.world.scores.ScoreHolder.forNameOnly(name),b.getObjective(o))!=null;}
    private static void draws(GameTestHelper h,Entity p,Set<Integer> expected,int count,String label){var seen=new HashSet<Integer>();for(int i=0;i<count;i++){command(p,"function "+V+"select_map");int got=score(p,"$selectedMap","CmdData");h.assertTrue(expected.contains(got),label+" chose ineligible "+got);seen.add(got);}h.assertTrue(seen.equals(expected),label+" must reach every eligible map: "+seen);}
    private static void command(Entity e,String text){e.getServer().getCommands().performPrefixedCommand(e.getServer().createCommandSourceStack().withEntity(e).withLevel((ServerLevel)e.level()).withPosition(e.position()).withPermission(4).withSuppressedOutput(),text);}
    private static ServerPlayer player(GameTestHelper h,String name){var profile=new GameProfile(UUID.randomUUID(),name);var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),profile,ClientInformation.createDefault());p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p,net.minecraft.server.network.CommonListenerCookie.createInitial(profile,false)){
        @Override public boolean hasChannel(net.minecraft.resources.ResourceLocation c){return false;}
        @Override public void send(net.minecraft.network.protocol.Packet<?> packet){}
        @Override public void send(net.minecraft.network.protocol.Packet<?> packet,net.minecraft.network.PacketSendListener listener){}
    };p.setClientLoaded(true);p.initInventoryMenu();h.getLevel().addNewPlayer(p);return p;}
    @SuppressWarnings("unchecked") private static List<ServerPlayer> players(GameTestHelper h){try{var f=net.minecraft.server.players.PlayerList.class.getDeclaredField("players");f.setAccessible(true);return (List<ServerPlayer>)f.get(h.getLevel().getServer().getPlayerList());}catch(Exception e){throw new RuntimeException(e);}}
}
