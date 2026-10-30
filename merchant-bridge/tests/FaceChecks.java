package backstabbed.regression;
import net.minecraft.network.Connection;
import net.minecraft.network.PacketSendListener;
import net.minecraft.network.protocol.Packet;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.network.CommonListenerCookie;
import net.minecraft.server.network.ServerGamePacketListenerImpl;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.bus.api.EventPriority;


import gravity_changer.api.GravityChangerAPI;
import net.minecraft.server.MinecraftServer;
import net.minecraft.core.Direction;
import net.minecraft.client.Minecraft;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import java.nio.file.*;
import java.util.*;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.level.GameType;
import net.minecraft.world.phys.Vec3;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.scores.ScoreHolder;
@Mod("backstabbed_regression")
public final class FaceChecks {
    int phase=0, ticks=0;
    final List<String> results=new ArrayList<>();
    public FaceChecks() {
        NeoForge.EVENT_BUS.addListener(this::tick);
        NeoForge.EVENT_BUS.addListener(EventPriority.HIGHEST, this::joining);
    }
    private void joining(PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer p && p.getTags().contains("backstabbed_local_dummy"))
            p.connection = new QuietListener(p.getServer(), p.connection.getConnection(), p,
                                            CommonListenerCookie.createInitial(p.getGameProfile(), false));
    }
    private static final class QuietListener extends ServerGamePacketListenerImpl {
        QuietListener(MinecraftServer s, Connection c, ServerPlayer p, CommonListenerCookie cookie) { super(s, c, p, cookie); }
        @Override public void send(Packet<?> packet) {}
        @Override public void send(Packet<?> packet, PacketSendListener listener) {}
        @Override public void tick() {}
    }

    void cmd(MinecraftServer s, ServerPlayer p, String command) {
        s.getCommands().performPrefixedCommand(p.createCommandSourceStack().withPermission(4).withSuppressedOutput(),command);
    }
    void check(boolean condition, String message) {
        if(!condition)throw new AssertionError(message);
        results.add(message);System.out.println("CUBE_FACE_CHECK "+message);
    }
    List<Entity> tagged(MinecraftServer s,String tag) {
        var list=new ArrayList<Entity>();
        for(var e:s.overworld().getAllEntities())if(!e.isRemoved()&&e.getTags().contains(tag))list.add(e);
        return list;
    }
    int score(MinecraftServer s,String name) {
        var v=s.getScoreboard().getPlayerScoreInfo(ScoreHolder.forNameOnly(name),s.getScoreboard().getObjective("CmdData"));
        return v==null?0:v.value();
    }
    void contacts(MinecraftServer s,ServerPlayer p) {
        cmd(s,p,"function cube_block:init");
        var markers=tagged(s,"PlayerSpawn");
        check(markers.size()==32,"32 spawn markers are active");
        p.setGameMode(GameType.ADVENTURE);
        var directions=new EnumMap<Direction,Integer>(Direction.class);
        for(var marker:markers) {
            var data=marker.saveWithoutId(new CompoundTag()).getCompound("data");
            var direction=Direction.byName(data.getString("gravity_direction"));
            directions.merge(direction,1,Integer::sum);
            markers.forEach(e->e.addTag("Occupied"));marker.removeTag("Occupied");
            cmd(s,p,"function mcm:maps/tptospawn");
            check(GravityChangerAPI.getBaseGravityDirection(p)==direction
                &&GravityChangerAPI.getGravityDirection(p)==direction
                &&GravityChangerAPI.getGravityComponent(p).getPrevGravityDirection()==direction,
                "Synchronous player gravity "+direction+" at "+marker.position());
            check(p.position().distanceTo(marker.position())<.0001,"Exact selected destination "+marker.position());
            check(s.overworld().noCollision(p,p.getBoundingBox()),"Native rotated player collision clear "+marker.position());
            var delta=new Vec3(direction.getStepX(),direction.getStepY(),direction.getStepZ()).scale(.02);
            check(s.overworld().getBlockCollisions(p,p.getBoundingBox().move(delta)).iterator().hasNext(),
                "Native rotated player support "+marker.position());
            check(marker.getTags().contains("Occupied")&&tagged(s,"CubeBlockSelectedSpawn").isEmpty(),
                "Selected spawn occupied and temporary selection cleared");
            check(marker.getTags().contains("ScrapSpawn"),"Scrap shares face contact");
            s.getCommands().performPrefixedCommand(s.createCommandSourceStack().withEntity(marker).withPosition(marker.position()).withPermission(4).withSuppressedOutput(),
                "function mcm:extensions/gravity/spawn_scrap");
            var scrap=tagged(s,"KeyItem").stream().filter(e->e instanceof ItemEntity).toList();
            check(scrap.size()==1&&GravityChangerAPI.getGravityDirection(scrap.getFirst())==direction,
                "Real scrap inherits "+direction);
            var item=scrap.getFirst();
            check(s.overworld().noCollision(item,item.getBoundingBox()),"Native scrap collision clear");
            check(s.overworld().getBlockCollisions(item,item.getBoundingBox().move(delta)).iterator().hasNext(),"Native scrap support");
            item.discard();
        }
        check(directions.size()==6&&directions.get(Direction.DOWN)==6&&directions.get(Direction.UP)==6
            &&directions.get(Direction.EAST)==5&&directions.get(Direction.WEST)==5
            &&directions.get(Direction.NORTH)==5&&directions.get(Direction.SOUTH)==5,
            "All six faces have the intended 6/6/5/5/5/5 distribution");
        cmd(s,p,"function mcm:maps/tptospawn");
        check(markers.stream().filter(e->e.getTags().contains("Occupied")).count()==1,
            "Exhausted occupancy pool refreshes before selecting another face");
        var before=p.position();var gravity=GravityChangerAPI.getBaseGravityDirection(p);
        var marker=markers.getFirst();var old=marker.saveWithoutId(new CompoundTag()).getCompound("data");
        cmd(s,p,"data merge entity "+marker.getUUID()+" {data:{gravity_direction:\"invalid\"}}");
        cmd(s,p,"arena_spawn_gravity "+marker.getUUID());
        check(p.position().equals(before)&&GravityChangerAPI.getBaseGravityDirection(p)==gravity,
            "Invalid marker gravity is rejected without changing player state");
        cmd(s,p,"data merge entity "+marker.getUUID()+" {data:"+old+"}");
        cmd(s,p,"scoreboard players set $selectedMap CmdData 22");
        cmd(s,p,"function mcm:maps/tptospawn");
        check(GravityChangerAPI.getBaseGravityDirection(p)==Direction.DOWN,"Other arenas retain ordinary downward spawning");
        cmd(s,p,"scoreboard players set $selectedMap CmdData 23");
        cmd(s,p,"function cube_block:activate");cmd(s,p,"function cube_block:activate");
        check(tagged(s,"PlayerSpawn").size()==32&&tagged(s,"ScrapSpawn").size()==32,"Repeated activation preserves exact marker counts");
    }
    void finish(Throwable failure) {
        phase=-1;
        try {Files.writeString(Path.of(System.getenv("ARENA_CHECK_DIR"),"results.txt"),
            (failure==null?"PASS\n":"FAIL "+failure+"\n")+String.join("\n",results)+"\n");}catch(Exception e){e.printStackTrace();}
        Minecraft.getInstance().execute(()->Minecraft.getInstance().stop());
    }
    void tick(ServerTickEvent.Post event) {
        if(phase<0)return;
        var s=event.getServer();var p=s.getPlayerList().getPlayerByName("PlaytestDummy1");
        if(p==null||s.getPlayerList().getPlayerCount()!=4)return;
        try {
            if(phase==0&&++ticks>=80) {
                cmd(s,p,"scoreboard players set $autostart GameRules 0");
                cmd(s,p,"scoreboard players set $gamestate CmdData 0");
                cmd(s,p,"function cube_block:select");ticks=0;phase=1;
            } else if(phase==1&&++ticks>=80) {
                contacts(s,p);
                cmd(s,p,"tag @a add queued");cmd(s,p,"tag @a add autoqueue");cmd(s,p,"tag @a remove spectating");
                cmd(s,p,"scoreboard players reset @a dead");cmd(s,p,"tag @a remove murderer");
                cmd(s,p,"tag @a remove gunner");cmd(s,p,"tag @a remove innocent");cmd(s,p,"team join nametags @a");
                cmd(s,p,"scoreboard players set $queued CmdData 4");cmd(s,p,"scoreboard players set $startcountdown CmdData 2");
                cmd(s,p,"scoreboard players set $start CmdData 1");cmd(s,p,"function mcm:lobby/start");ticks=0;phase=2;
            } else if(phase==2&&++ticks>=400) {
                check(score(s,"$gamestate")==1&&score(s,"$selectedMap")==23,"Normal four-player round survives role assignment and grace period");
                for(var player:s.getPlayerList().getPlayers()) {
                    check(!player.isSpectator()&&player.getTags().contains("CubeBlockHook"),"Living player retains grappler: "+player.getGameProfile().getName());
                    check(s.overworld().noCollision(player,player.getBoundingBox()),"Player remains collision clear after gravity ticks: "+player.getGameProfile().getName());
                }
                cmd(s,p,"scoreboard players set $gameEndTimer CmdData 1");cmd(s,p,"function mcm:game/loops/gameend");
                check(tagged(s,"CubeBlockRuntime").isEmpty(),"Normal round-end reset cleans markers");
                for(var player:s.getPlayerList().getPlayers())
                    check(GravityChangerAPI.getBaseGravityDirection(player)==Direction.DOWN,"Lobby return resets gravity: "+player.getGameProfile().getName());
                finish(null);
            }
        }catch(Throwable failure){failure.printStackTrace();finish(failure);}
    }
}
