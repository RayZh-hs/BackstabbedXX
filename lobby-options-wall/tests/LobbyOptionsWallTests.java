package gravity_changer.test;

import java.util.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.*;
import net.minecraft.world.entity.*;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

@net.neoforged.fml.common.EventBusSubscriber(modid="gravity_changer", bus=net.neoforged.fml.common.EventBusSubscriber.Bus.MOD)
@PrefixGameTestTemplate(false)
public final class LobbyOptionsWallTests {
    private static final String BASE = "mcm:lobby/options/ext_wall/";
    @net.neoforged.bus.api.SubscribeEvent
    public static void register(net.neoforged.neoforge.event.RegisterGameTestsEvent event) { event.register(LobbyOptionsWallTests.class); }

    @GameTest(template="empty", templateNamespace="gravity_changer", batch="options_wall", timeoutTicks=300)
    public static void completeOptionsWall(GameTestHelper h) {
        var level = h.getLevel();
        var forced = new ArrayList<net.minecraft.world.level.ChunkPos>();
        for (int x=1; x<=2; x++) for (int z=5; z<=8; z++) {
            var pos = new net.minecraft.world.level.ChunkPos(x,z);
            if (!level.getForcedChunks().contains(pos.toLong())) { level.setChunkForced(x,z,true); forced.add(pos); }
            level.getChunk(x,z);
        }
        h.runAfterDelay(10, () -> {
            // GameTest runs at a random remote origin; explicitly expose the fixed lobby fixture.
            try {
                var field=ServerLevel.class.getDeclaredField("entityManager"); field.setAccessible(true);
                @SuppressWarnings("unchecked") var manager=(net.minecraft.world.level.entity.PersistentEntitySectionManager<Entity>)field.get(level);
                for(int x=1;x<=2;x++) for(int z=5;z<=8;z++) manager.updateChunkStatus(new net.minecraft.world.level.ChunkPos(x,z),net.minecraft.world.level.entity.Visibility.TICKING);
            } catch(ReflectiveOperationException e) {throw new RuntimeException(e);}
            var p = player(h,"WallClicker"); var other = player(h,"WallBystander");
            var online = players(h); online.add(p); online.add(other);
            try {
                p.setPos(25,8,112.5); other.setPos(27,8,112.5);
                for (String o : List.of("CmdData","GameRules","temp","math")) command(p,"scoreboard objectives add "+o+" dummy");
                command(p,"scoreboard objectives remove mcm_options");
                command(p,"scoreboard objectives add mcm_options trigger");
                command(p,"scoreboard players set $gamestate CmdData 0");
                command(p,"scoreboard players set $twenty math 20");
                command(p,"data modify storage mcm:options options set value {autostart:1,murderers:{value:1,smart:0},gametime:{value:6},animations:1,scrap_start:1,murderer_ff:0,update_ingame_counts:1,darkness:0,recall_destroy_guns:0}");
                command(p,"function mcm:extensions/options/init");
                command(p,"execute positioned 27.4 9.75 84.5 run function mcm:lobby/options/summon_interaction {data:{Tags:[\"LegacyResetFixture\"],width:1f,height:0.6f,response:1b},callback:\"mcm:lobby/options/reset_to_defaults\",extra:{}}");
                command(p,"summon text_display 26.9 9.75 84.5 {Tags:[\"option\",\"LegacyResetFixture\"],text:'\"Reset\"'}");
                command(p,"summon text_display 26.9 9.75 85.5 {Tags:[\"option\",\"KeepOptionFixture\"],text:'\"Keep\"'}");
                command(p,"function "+BASE+"install");
                h.assertTrue(level.getEntities(EntityType.INTERACTION,e->e.getTags().contains("LegacyResetFixture")).isEmpty() && level.getEntities(EntityType.TEXT_DISPLAY,e->e.getTags().contains("LegacyResetFixture")).isEmpty(),"Legacy reset button and label are removed");
                h.assertTrue(level.getEntities(EntityType.TEXT_DISPLAY,e->e.getTags().contains("KeepOptionFixture")).size()==1,"Adjacent unrelated controls remain");
                var modePanel=displays(h).stream().filter(e->e.getTags().contains("McmWall_mode")).findFirst().orElseThrow();
                h.assertTrue(Math.abs(modePanel.getX()-26.86)<.00001 && Math.abs(modePanel.getZ()-84.5)<.00001,"Mode selector is on the negative-Z upstairs wall");
                h.assertTrue(displays(h).size()==26 && controls(h).size()==21,"Expected 26 displays / 21 controls, got "+displays(h).size()+" / "+controls(h).size());
                for (var d : displays(h)) h.assertTrue(Math.abs(d.getYRot()-90)<.001,"Panels must face the lobby aisle");
                Set<Integer> actions = new HashSet<>();
                for (var i : controls(h)) actions.add(action(i));
                for (int n=2;n<=22;n++) h.assertTrue(actions.contains(n),"Missing physical action "+n);

                command(other,"scoreboard players set @s mcm_options 777");
                click(h,p,other,2);
                h.assertTrue(score(p,"$shield")==1,"Shield toggle must change the existing setting");
                h.assertTrue(playerScore(other,"mcm_options")==777 && playerScore(p,"mcm_options")==0,
                    "Use the recorded clicker UUID, not nearest player or callback executor");
                h.assertTrue(text(h,"shield").contains("开启"),"Wall value refreshes after click");

                click(h,p,other,4); click(h,p,other,5);
                h.assertTrue(score(p,"$craft_keep")==0 && score(p,"$ammo")==0,"Missing scrap prerequisite must reject both actions");
                click(h,p,other,3); click(h,p,other,4); click(h,p,other,5);
                h.assertTrue(score(p,"$gunner_scrap")==1 && score(p,"$craft_keep")==1 && score(p,"$ammo")==1,"Dependent options enable correctly");
                click(h,p,other,3);
                h.assertTrue(score(p,"$craft_keep")==0 && score(p,"$ammo")==0,"Disabling prerequisite normalizes both dependent settings");
                h.assertTrue(control(h,4).saveWithoutId(new CompoundTag()).getFloat("width")==0 && text(h,"craft_keep").contains("需先开启"),"Disabled controls and explanation agree");

                for (var entry : Map.of(6,"$knife_timeout",10,"$global_glow",11,"$team_sight",12,"$gun_glow").entrySet()) {
                    click(h,p,other,entry.getKey()); h.assertTrue(score(p,entry.getValue())==1,"Toggle "+entry.getKey());
                }
                click(h,p,other,14); h.assertTrue(score(p,"$scrap_boost")==0,"Default-enabled opening boost toggles off");
                click(h,p,other,7); h.assertTrue(score(p,"$knife_seconds")==14,"Minus one second");
                click(h,p,other,8); h.assertTrue(score(p,"$knife_seconds")==15,"Plus one second");
                for (int bound : new int[]{5,30}) {
                    command(p,"data modify storage mcm:options options.ext.knife_seconds set value "+bound);
                    command(p,"function mcm:extensions/options/sync");
                    int action=bound==5?7:8;
                    h.assertTrue(control(h,action).saveWithoutId(new CompoundTag()).getFloat("width")==0,"Limit button is disabled at "+bound);
                    click(h,p,other,action); h.assertTrue(score(p,"$knife_seconds")==bound,"Knife timeout remains in bounds");
                }
                var rewards = new HashSet<Integer>();
                var rates = new HashSet<Integer>();
                for(int n=0;n<5;n++) {click(h,p,other,9); rewards.add(score(p,"$kill_reward")); click(h,p,other,13); rates.add(score(p,"$scrap_rate"));}
                h.assertTrue(rewards.equals(Set.of(-1,0,2,3,5)),"All kill reward choices are reachable");
                h.assertTrue(rates.equals(Set.of(50,80,100,150,200)),"All spawn multiplier choices are reachable");
                for(int n=15;n<=17;n++) {click(h,p,other,n); h.assertTrue(score(p,"$mode")==n-15,"Mode selector "+n);}
                int[] respawn={3,5,10,20,30};
                for(int n=18;n<=22;n++) {click(h,p,other,n);h.assertTrue(score(p,"$gunner_respawn")==respawn[n-18],"Respawn selector "+n);}

                command(p,"scoreboard players set @s mcm_options 2");
                command(p,"function mcm:extensions/options/change");
                command(p,"scoreboard players set @s mcm_options 0");
                h.assertTrue(score(p,"$shield")==0 && text(h,"shield").contains("关闭"),"Chat menu updates physical wall");
                command(p,"function mcm:lobby/options/lock_options");
                h.assertTrue(control(h,2).saveWithoutId(new CompoundTag()).getFloat("width")==0 && text(h,"shield").contains("已锁定"),"Lobby lock reaches new controls");
                click(h,p,other,2); h.assertTrue(score(p,"$shield")==0,"Locked settings cannot change");
                command(p,"function mcm:lobby/options/unlock_options");
                command(other,"scoreboard players set @s mcm_options 0");
                command(p,"scoreboard players set $gamestate CmdData 1"); command(p,"function mcm:extensions/tick");
                click(h,p,other,2); h.assertTrue(score(p,"$shield")==0 && control(h,2).saveWithoutId(new CompoundTag()).getFloat("width")==0,"In-game edits are rejected");
                command(p,"scoreboard players set $gamestate CmdData -1"); command(p,"function mcm:extensions/tick");
                h.assertTrue(control(h,2).saveWithoutId(new CompoundTag()).getFloat("width")==3,"Returning to voting re-enables controls automatically");
                click(h,p,other,2); h.assertTrue(score(p,"$shield")==1,"Voting permits option changes");
                command(p,"scoreboard players set $gamestate CmdData 0"); command(p,"function mcm:extensions/tick");
                h.assertTrue(control(h,2).saveWithoutId(new CompoundTag()).getFloat("width")==3,"Preparation keeps controls enabled");
                command(p,"function "+BASE+"install"); command(p,"function "+BASE+"install");
                h.assertTrue(displays(h).size()==26 && controls(h).size()==21,"Repeated installation must not duplicate panels");
                h.assertTrue(score(p,"$mode")==2 && score(p,"$gunner_respawn")==30,"Installation preserves user settings");
                command(p,"function mcm:lobby/options/reset_to_defaults");
                h.assertTrue(score(p,"$shield")==0 && score(p,"$gunner_scrap")==0 && score(p,"$scrap_rate")==100
                    && score(p,"$scrap_boost")==1 && score(p,"$mode")==0,"Reset restores existing defaults");
                h.assertTrue(displays(h).size()==26 && controls(h).size()==21,"Reset does not duplicate physical panels");
                System.out.println("OPTIONS_WALL_PASS all actions, ownership, bounds, dependencies, lock, in-game guard, chat refresh, reset and reinstall");
            } finally {
                command(p,"execute as @e[tag=McmOptionsWall] on passengers run kill @s");
                command(p,"kill @e[tag=McmOptionsWall]");
                command(p,"kill @e[tag=KeepOptionFixture]");
                command(p,"scoreboard players set $gamestate CmdData 0");
                online.remove(p); online.remove(other); p.discard(); other.discard();
                for (var pos : forced) level.setChunkForced(pos.x,pos.z,false);
            }
            h.succeed();
        });
    }

    private static List<? extends Display.TextDisplay> displays(GameTestHelper h) {return h.getLevel().getEntities(EntityType.TEXT_DISPLAY,e->e.getTags().contains("McmOptionsWall"));}
    private static List<? extends Interaction> controls(GameTestHelper h) {return h.getLevel().getEntities(EntityType.INTERACTION,e->e.getTags().contains("McmOptionsWall"));}
    private static int action(Interaction i) {return i.getFirstPassenger().saveWithoutId(new CompoundTag()).getCompound("data").getInt("action");}
    private static Interaction control(GameTestHelper h,int n) {return controls(h).stream().filter(e->action(e)==n).findFirst().orElseThrow();}
    private static String text(GameTestHelper h,String key) {return displays(h).stream().filter(e->e.getTags().contains("McmWall_"+key)).findFirst().orElseThrow().saveWithoutId(new CompoundTag()).getString("text");}
    private static int score(Entity e,String name) {var b=e.getServer().getScoreboard();return b.getOrCreatePlayerScore(net.minecraft.world.scores.ScoreHolder.forNameOnly(name),b.getObjective("GameRules")).get();}
    private static int playerScore(Entity e,String name) {var b=e.getServer().getScoreboard();return b.getOrCreatePlayerScore(e,b.getObjective(name)).get();}
    private static void click(GameTestHelper h,ServerPlayer p,ServerPlayer other,int n) {
        var interaction=control(h,n); var record=new CompoundTag();record.putUUID("player",p.getUUID());record.putLong("timestamp",h.getLevel().getGameTime());
        command(interaction,"data modify entity @s interaction set value "+record);
        command(other,"function mcm:lobby/options/backend/click");
        h.assertTrue(!interaction.saveWithoutId(new CompoundTag()).contains("interaction"),"Click record must be consumed once");
    }
    private static void command(Entity e,String text) {e.getServer().getCommands().performPrefixedCommand(e.getServer().createCommandSourceStack().withEntity(e).withLevel((ServerLevel)e.level()).withPosition(e.position()).withPermission(4).withSource(new net.minecraft.commands.CommandSource() {
        public void sendSystemMessage(net.minecraft.network.chat.Component message) {System.out.println("WALL_COMMAND "+text+": "+message.getString());}
        public boolean acceptsSuccess() {return false;}
        public boolean acceptsFailure() {return true;}
        public boolean shouldInformAdmins() {return false;}
    }),text);}
    private static ServerPlayer player(GameTestHelper h,String name) {
        var profile=new GameProfile(UUID.randomUUID(),name);var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),profile,ClientInformation.createDefault());
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p,net.minecraft.server.network.CommonListenerCookie.createInitial(profile,false)) {
            @Override public boolean hasChannel(net.minecraft.resources.ResourceLocation c) {return false;}
            @Override public void send(net.minecraft.network.protocol.Packet<?> packet) {}
            @Override public void send(net.minecraft.network.protocol.Packet<?> packet,net.minecraft.network.PacketSendListener listener) {}
        };
        p.setClientLoaded(true);p.initInventoryMenu();h.getLevel().addNewPlayer(p);return p;
    }
    @SuppressWarnings("unchecked") private static List<ServerPlayer> players(GameTestHelper h) {
        try {var f=net.minecraft.server.players.PlayerList.class.getDeclaredField("players");f.setAccessible(true);return (List<ServerPlayer>)f.get(h.getLevel().getServer().getPlayerList());}
        catch(Exception e) {throw new RuntimeException(e);}
    }
}
