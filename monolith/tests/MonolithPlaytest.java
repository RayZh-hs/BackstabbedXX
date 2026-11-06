package backstabbed.regression;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.network.protocol.common.ClientboundCustomPayloadPacket;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.GameType;
import net.minecraft.world.scores.ScoreHolder;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.network.registration.NetworkRegistry;

@Mod("backstabbed_regression")
public final class MonolithPlaytest {
    private int phase=0,ticks=0,pictureIndex=0;
    private volatile boolean clientHasPotion=false,clientPotionCooldown=false;
    private final java.util.List<String> clientChat=new java.util.concurrent.CopyOnWriteArrayList<>();
    private long naturalEnd=0, firstCD=0;
    private boolean naturalChecked=false,reloadRequested=false;
    private final List<String> results=new ArrayList<>();
    public MonolithPlaytest(){NeoForge.EVENT_BUS.addListener(EventPriority.LOWEST,this::tick);NeoForge.EVENT_BUS.addListener(this::chat);}
    private void chat(net.neoforged.neoforge.client.event.ClientChatReceivedEvent.System e){clientChat.add(e.getMessage().getString());}
    private record LoginPayloadProbe(String id) implements CustomPacketPayload {
        public Type<LoginPayloadProbe> type() { return new Type<>(ResourceLocation.parse(id)); }
    }
    private void checkLocalConnections(MinecraftServer server) {
        for (String name : List.of("PlaytestDummy1", "PlaytestDummy2", "PlaytestDummy3")) {
            var dummy = server.getPlayerList().getPlayerByName(name);
            check(dummy.connection.getClass().getName().equals("backstabbed.local.LocalPlaytest$IdleListener"),
                name + ": uses the production local helper listener, without test replacements");
            for (String channel : List.of("gravity_changer:entity_gravity", "mcmhighlight:highlight_delta")) {
                var payload = new LoginPayloadProbe(channel);
                var packet = new ClientboundCustomPayloadPacket(payload);
                boolean rejected = false;
                try { NetworkRegistry.checkPacket(packet, dummy.connection); }
                catch (UnsupportedOperationException expected) { rejected = true; }
                check(rejected, name + ": NeoForge rejects the unnegotiated " + channel + " channel");
                PacketDistributor.sendToPlayer(dummy, payload);
                dummy.connection.send(packet, null);
                check(true, name + ": both production send paths discard " + channel + " safely");
            }
        }
        check(!server.getPlayerList().getPlayerByName("BackstabbedDev").connection.getClass().getName()
            .contains("IdleListener"), "Real player retains the normal negotiated network connection");
    }
    private void cmd(MinecraftServer s,String c){s.getCommands().performPrefixedCommand(s.createCommandSourceStack().withPermission(4).withSuppressedOutput(),c);}
    private void check(boolean b,String m){if(!b)throw new AssertionError(m);results.add(m);System.out.println("MONOLITH_CHECK "+m);}
    private int score(MinecraftServer s,String h,String o){var v=s.getScoreboard().getPlayerScoreInfo(ScoreHolder.forNameOnly(h),s.getScoreboard().getObjective(o));return v==null?0:v.value();}
    private List<Entity> tagged(MinecraftServer s,String t){var out=new ArrayList<Entity>();for(var e:s.overworld().getAllEntities())if(e.getTags().contains(t))out.add(e);return out;}
    private void prepare(MinecraftServer s,ServerPlayer p){p.setGameMode(GameType.ADVENTURE);p.setShiftKeyDown(false);cmd(s,"tag "+p.getScoreboardName()+" add queued");cmd(s,"tag "+p.getScoreboardName()+" remove spectating");cmd(s,"scoreboard players set "+p.getScoreboardName()+" dead 0");cmd(s,"scoreboard players set $selectedMap CmdData 24");cmd(s,"scoreboard players set $gamestate CmdData 1");cmd(s,"scoreboard players set $graceperiod CmdData 0");p.addTag("MonolithParticipant");}
    private net.minecraft.world.item.ItemStack potion(ServerPlayer p){for(int i=0;i<p.getInventory().getContainerSize();i++){var q=p.getInventory().getItem(i);if(backstabbed.merchants.Monolith.isPotion(q))return q;}return net.minecraft.world.item.ItemStack.EMPTY;}
    private boolean clearRay(MinecraftServer s,ServerPlayer p,net.minecraft.world.phys.Vec3 a,net.minecraft.world.phys.Vec3 b){return s.overworld().clip(new net.minecraft.world.level.ClipContext(a,b,net.minecraft.world.level.ClipContext.Block.VISUAL,net.minecraft.world.level.ClipContext.Fluid.NONE,p)).getType()==net.minecraft.world.phys.HitResult.Type.MISS;}
    private void diagnoseVisibility(MinecraftServer s,ServerPlayer p){
        var points=tagged(s,"MonolithAltar");var cherry=points.stream().filter(e->e.getTags().contains("MonolithAltar2")).findFirst().orElseThrow();var base=cherry.position();
        var candidates=new ArrayList<net.minecraft.world.phys.Vec3>();
        for(int dx=-6;dx<=6;dx++)for(int dz=-5;dz<=5;dz++)for(int dy=0;dy<=6;dy++){
            var pos=base.add(dx,dy,dz);p.setPos(pos);var bb=p.getBoundingBox();if(!s.overworld().noCollision(p,bb)||!s.overworld().getBlockCollisions(p,bb.move(0,-.03,0)).iterator().hasNext())continue;
            boolean clear=true;for(var other:points)if(other!=cherry&&!clearRay(s,p,pos.add(0,1.27,0),backstabbed.merchants.Monolith.targetCenter((net.minecraft.world.entity.Marker)other)))clear=false;
            if(clear)candidates.add(pos);
        }
        candidates.sort(java.util.Comparator.comparingDouble(v->v.distanceToSqr(base)));for(var q:candidates.stream().limit(15).toList())results.add("CANDIDATE_CHERRY_LANDING "+q);
        var center=backstabbed.merchants.Monolith.runeCenter((net.minecraft.world.entity.Marker)cherry);var targets=new ArrayList<net.minecraft.world.phys.Vec3>();
        for(int dx=-4;dx<=4;dx++)for(int dy=-3;dy<=4;dy++)if(dx*dx+dy*dy<=16){var q=center.add(dx,dy,0);boolean clear=true;for(var other:points)if(other!=cherry&&!clearRay(s,p,other.position().add(0,1.27,0),q))clear=false;if(clear)targets.add(q);}
        targets.sort(java.util.Comparator.comparingDouble(v->v.distanceToSqr(center)));for(var q:targets.stream().limit(15).toList())results.add("CANDIDATE_CHERRY_TARGET "+q);
    }
    private void faceAltar(MinecraftServer s,ServerPlayer h,int index){
        var platforms=tagged(s,"MonolithAltar");var origin=platforms.stream().filter(e->e.getTags().contains("MonolithAltar"+index)).findFirst().orElseThrow(()->new AssertionError("Missing altar "+index+" among "+platforms));var look=net.minecraft.world.phys.Vec3.ZERO;
        for(var e:platforms)if(e!=origin)look=look.add(backstabbed.merchants.Monolith.targetCenter((net.minecraft.world.entity.Marker)e).subtract(origin.position().add(0,1.62,0)).normalize());
        look=look.normalize();h.teleportTo(s.overworld(),origin.getX(),origin.getY(),origin.getZ(),java.util.Set.of(),(float)Math.toDegrees(Math.atan2(-look.x,look.z)),(float)-Math.toDegrees(Math.asin(look.y)),false);h.setOnGround(true);
    }
    private void picture(String name){Minecraft.getInstance().execute(()->{var m=Minecraft.getInstance();m.options.hideGui=true;try{Files.writeString(Path.of(System.getenv("ARENA_CHECK_DIR"),name+"-camera.txt"),"Client "+m.player.position()+" yaw "+m.player.getYRot()+" pitch "+m.player.getXRot()+" camera "+m.getCameraEntity().position()+" gravity "+gravity_changer.api.GravityChangerAPI.getGravityDirection(m.player));}catch(Exception ex){throw new RuntimeException(ex);}Screenshot.grab(Path.of(System.getenv("ARENA_CHECK_DIR")).toFile(),name+".png",m.getMainRenderTarget(),x->{});});}
    private void tick(ServerTickEvent.Post event){if(phase<0)return;var s=event.getServer();var p=s.getPlayerList().getPlayerByName("PlaytestDummy1");if(p==null||s.getPlayerList().getPlayerCount()!=4)return;try{
        if(phase==0){if(++ticks<80)return;
            checkLocalConnections(s);
            for(String id:Files.readAllLines(Path.of(System.getenv("ARENA_CHECK_DIR"),"functions.txt")))check(s.getFunctions().get(ResourceLocation.parse(id)).isPresent(),"Parsed "+id);
            cmd(s,"scoreboard players set $autostart GameRules 0");cmd(s,"scoreboard players set $gamestate CmdData 0");cmd(s,"function monolith:select");phase=System.getenv("MONOLITH_CLIENT_POTION_ONLY")!=null?60:(System.getenv("MONOLITH_VISUAL_ONLY")!=null?40:1);ticks=0;
        }else if(phase==1&&++ticks>=80){
            check(score(s,"$selectedMap","CmdData")==24,"Selection goes through normal voting");check(tagged(s,"MonolithPoster").size()>=1,"One correctly wired poster display");
            var points=tagged(s,"PlayerSpawn");check(points.size()==36,"36 distributed player spawns");
            for(var e:points){p.setPos(e.position());check(s.overworld().noCollision(p,p.getBoundingBox()),"Clear native player volume "+e.position());check(s.overworld().getBlockCollisions(p,p.getBoundingBox().move(0,-.03,0)).iterator().hasNext(),"Native support "+e.position());
                int ways=0;for(int[] dir:new int[][]{{1,0},{-1,0},{0,1},{0,-1}}){boolean valid=false;for(int dy=-1;dy<=1;dy++){var bb=p.getBoundingBox().move(dir[0],dy,dir[1]);if(s.overworld().noCollision(p,bb)&&s.overworld().getBlockCollisions(p,bb.move(0,-.03,0)).iterator().hasNext())valid=true;}if(valid)ways++;}check(ways>=2,"At least two onward routes "+e.position());}
            check(tagged(s,"MonolithAltar").size()==3,"Three summit altars");
            var platforms=tagged(s,"MonolithAltar");boolean visible=true;
            for(var from:platforms)for(var to:platforms)if(from!=to){
                var eye=from.position().add(0,1.27,0);var targetCenter=backstabbed.merchants.Monolith.targetCenter((net.minecraft.world.entity.Marker)to);
                var hit=s.overworld().clip(new net.minecraft.world.level.ClipContext(eye,targetCenter,net.minecraft.world.level.ClipContext.Block.VISUAL,net.minecraft.world.level.ClipContext.Fluid.NONE,p));
                results.add("Sightline "+from.position()+" -> "+targetCenter+": "+hit.getType()+" "+hit.getBlockPos());if(hit.getType()!=net.minecraft.world.phys.HitResult.Type.MISS)visible=false;
            }

            if(!visible)diagnoseVisibility(s,p);check(visible,"All six altar sightlines are unobstructed");
            var altars=tagged(s,"MonolithAltar");for(var a:altars){p.setPos(a.position());check(s.overworld().noCollision(p,p.getBoundingBox())&&s.overworld().getBlockCollisions(p,p.getBoundingBox().move(0,-.03,0)).iterator().hasNext(),"Safe summit landing "+a.position());}
            cmd(s,"function monolith:activate");check(tagged(s,"PlayerSpawn").size()==36&&tagged(s,"MonolithAltar").size()==3,"Repeated activation is idempotent");
            cmd(s,"tag @a add queued");cmd(s,"tag @a add autoqueue");cmd(s,"tag @a remove spectating");cmd(s,"scoreboard players reset @a dead");cmd(s,"team join nametags @a");cmd(s,"scoreboard players set $queued CmdData 4");cmd(s,"scoreboard players set $startcountdown CmdData 2");cmd(s,"scoreboard players set $start CmdData 1");cmd(s,"function mcm:lobby/start");phase=2;ticks=0;
        }else if(phase==2&&++ticks>=400){
            check(score(s,"$gamestate","CmdData")==1,"Real four-player round survives grace and role assignment");for(var a:s.getPlayerList().getPlayers())check(!potion(a).isEmpty(),"Reusable potion survives role loadout: "+a.getScoreboardName());
            var altar=tagged(s,"MonolithAltar").getFirst();prepare(s,p);p.teleportTo(altar.getX(),altar.getY(),altar.getZ());p.setOnGround(true);p.setShiftKeyDown(true);cmd(s,"monolith tick");check(p.hasEffect(net.minecraft.world.effect.MobEffects.DARKNESS),"Sneaking on summit applies darkness and constructs private rune packets");
            var markers=tagged(s,"MonolithAltar").stream().map(e->(net.minecraft.world.entity.Marker)e).sorted(java.util.Comparator.comparingInt(e->e.getTags().contains("MonolithAltar0")?0:e.getTags().contains("MonolithAltar1")?1:2)).toList();var target=markers.get(1);var eye=p.getEyePosition();var look=backstabbed.merchants.Monolith.targetCenter(target).subtract(eye).normalize();check(backstabbed.merchants.Monolith.target(eye,look,markers,0)==1,"Aim cone chooses viewed altar");check(backstabbed.merchants.Monolith.target(eye,new net.minecraft.world.phys.Vec3(1,0,0),markers,0)==-1,"Aim away has no destination");
            float yaw=(float)Math.toDegrees(Math.atan2(-look.x,look.z));float pitch=(float)-Math.toDegrees(Math.asin(look.y));p.setYRot(yaw);p.setXRot(pitch);p.setShiftKeyDown(false);cmd(s,"monolith tick");check(p.position().distanceTo(target.position())<.01,"Releasing sneak travels to the aimed summit");check(!p.hasEffect(net.minecraft.world.effect.MobEffects.DARKNESS),"Release clears travel darkness");
            var facing=net.minecraft.world.phys.Vec3.ZERO;for(var other:markers)if(other!=target)facing=facing.add(backstabbed.merchants.Monolith.targetCenter(other).subtract(p.getEyePosition()).normalize());check(p.getLookAngle().dot(facing.normalize())>.999,"Travel arrival faces the two remaining islands");
            // Native use pipeline: hold the actual map potion until LivingEntity finishes it.
            p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,potion(p).copy());p.startUsingItem(net.minecraft.world.InteractionHand.MAIN_HAND);phase=3;ticks=0;
        }else if(phase==3&&++ticks>=34){
            check(p.hasEffect(net.minecraft.world.effect.MobEffects.LEVITATION),"Native drinking starts levitation");check(backstabbed.merchants.Monolith.isPotion(p.getMainHandItem()),"Native finish returns the reusable potion instead of a glass bottle");long now=s.overworld().getGameTime();long cd=p.getPersistentData().getLong("MonolithCooldownUntil");check(cd-now>=595&&cd-now<=600,"Cooldown starts at float activation for 600 ticks");check(p.getPersistentData().getLong("MonolithFloatUntil")-now>=95,"Float duration is 100 ticks");
            p.setOnGround(false);p.setShiftKeyDown(true);cmd(s,"monolith tick");check(!p.hasEffect(net.minecraft.world.effect.MobEffects.LEVITATION),"Midair sneak cancels levitation");check(p.getPersistentData().getLong("MonolithCooldownUntil")==cd,"Cancellation retains original cooldown deadline");p.setShiftKeyDown(false);
            var q=s.getPlayerList().getPlayerByName("PlaytestDummy2");check(!q.getPersistentData().contains("MonolithCooldownUntil"),"Cooldown is independent per player");
            var right=new net.neoforged.neoforge.event.entity.player.PlayerInteractEvent.RightClickItem(p,net.minecraft.world.InteractionHand.MAIN_HAND);NeoForge.EVENT_BUS.post(right);check(right.isCanceled(),"Cooldown refuses another drink");
            firstCD=cd;
            prepare(s,q);var a=tagged(s,"MonolithAltar").get(1);q.teleportTo(a.getX(),a.getY(),a.getZ());q.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,potion(q).copy());q.startUsingItem(net.minecraft.world.InteractionHand.MAIN_HAND);phase=30;ticks=0;
        }else if(phase==30&&++ticks>=34){
            var q=s.getPlayerList().getPlayerByName("PlaytestDummy2");check(q.hasEffect(net.minecraft.world.effect.MobEffects.LEVITATION),"Second player can independently drink during first player's cooldown");naturalEnd=q.getPersistentData().getLong("MonolithFloatUntil");phase=31;ticks=0;
        }else if(phase==31){
            var q=s.getPlayerList().getPlayerByName("PlaytestDummy2");long now=s.overworld().getGameTime();
            if(now<naturalEnd)check(q.hasEffect(net.minecraft.world.effect.MobEffects.LEVITATION),"Float remains active through tick "+(100-(naturalEnd-now)));
            if(now>=naturalEnd&&!naturalChecked){check(!q.hasEffect(net.minecraft.world.effect.MobEffects.LEVITATION),"Natural expiry clears float at exactly 100 ticks");naturalChecked=true;}
            if(now>=firstCD-200&&!reloadRequested){cmd(s,"reload");reloadRequested=true;}
            if(now<firstCD)return;
            check(tagged(s,"MonolithRuntime").size()==40,"Active reload preserves exactly one set of arena markers");
            check(p.getPersistentData().getLong("MonolithCooldownUntil")==firstCD,"Reload preserves the cooldown deadline");
            check(!p.getCooldowns().isOnCooldown(potion(p)),"Original potion is ready exactly 600 ticks after activation");
            // End-to-end escape policy: waiting and grace return, round play eliminates, spectator and other maps ignored.
            cmd(s,"scoreboard players set $gamestate CmdData 0");p.teleportTo(53230,100,53350);cmd(s,"function monolith:waiting_tick");check(p.getY()>=118&&!p.isSpectator(),"Waiting void escape returns safely");
            prepare(s,p);cmd(s,"scoreboard players set $graceperiod CmdData 50");p.teleportTo(53230,100,53350);cmd(s,"function monolith:functionality");check(p.getY()>=118&&!p.isSpectator(),"Grace void escape returns safely");
            cmd(s,"scoreboard players set $graceperiod CmdData 0");p.teleportTo(53230,100,53350);cmd(s,"function monolith:functionality");check(score(s,p.getScoreboardName(),"dead")==1&&p.isSpectator(),"Active void escape eliminates");cmd(s,"monolith tick");check(potion(p).isEmpty()&&!p.getPersistentData().contains("MonolithCooldownUntil"),"Death cleans potion and mobility state");
            prepare(s,p);p.setGameMode(GameType.SPECTATOR);p.teleportTo(53230,100,53350);cmd(s,"function monolith:functionality");check(p.getY()==100,"Native spectators bypass containment");
            prepare(s,p);cmd(s,"scoreboard players set $selectedMap CmdData 22");p.teleportTo(53230,100,53350);cmd(s,"function monolith:functionality");check(p.getY()==100,"Other arenas bypass Monolith containment");
            cmd(s,"scoreboard players set $selectedMap CmdData 24");cmd(s,"function monolith:reset");check(tagged(s,"MonolithRuntime").isEmpty(),"Reset removes runtime entities");cmd(s,"function monolith:activate");check(tagged(s,"MonolithRuntime").size()==40,"Reactivation rebuilds exactly 36 spawns, 3 altars, 1 spectator");
            cmd(s,"tag BackstabbedDev remove queued");cmd(s,"tag BackstabbedDev remove autoqueue");cmd(s,"tag BackstabbedDev add spectating");cmd(s,"tag BackstabbedDev remove MonolithParticipant");cmd(s,"gamemode spectator BackstabbedDev");cmd(s,"tp BackstabbedDev 53290 170 53390 65 20");cmd(s,"scoreboard players set $gamestate CmdData -2");phase=40;ticks=0;
        }else if(phase==60&&++ticks>=80){
            var h=s.getPlayerList().getPlayerByName("BackstabbedDev");prepare(s,h);cmd(s,"tag @a add queued");cmd(s,"tag @a remove spectating");cmd(s,"tag @a add autoqueue");cmd(s,"tag @a remove murderer");cmd(s,"tag @a add innocent");cmd(s,"tag BackstabbedDev remove innocent");cmd(s,"tag BackstabbedDev add murderer");cmd(s,"scoreboard players set $pickedroles CmdData 1");cmd(s,"scoreboard players set $graceperiod CmdData 0");cmd(s,"scoreboard players set $start CmdData 0");
            cmd(s,"scoreboard players set $gametimer CmdData 12000");cmd(s,"scoreboard players set @a dead 0");var starts=tagged(s,"PlayerSpawn");int si=0;for(var player:s.getPlayerList().getPlayers()){player.teleportTo(starts.get(si).getX(),starts.get(si).getY(),starts.get(si++).getZ());}
            cmd(s,"monolith cleanup");h.getInventory().clearContent();cmd(s,"execute as BackstabbedDev run function monolith:equipment");var altar=tagged(s,"MonolithAltar").get(1);h.teleportTo(s.overworld(),altar.getX(),altar.getY(),altar.getZ(),java.util.Set.of(),0,0,false);h.getInventory().selected=0;h.inventoryMenu.sendAllDataToRemote();phase=61;ticks=0;
        }else if(phase==61&&++ticks>=20){
            Minecraft.getInstance().execute(()->{var mc=Minecraft.getInstance();mc.options.keyUse.setDown(true);mc.gameMode.useItem(mc.player,net.minecraft.world.InteractionHand.MAIN_HAND);});phase=62;ticks=0;
        }else if(phase==62&&++ticks>=40){
            var h=s.getPlayerList().getPlayerByName("BackstabbedDev");check(h.getPersistentData().contains("MonolithCooldownUntil"),"Real client drinking reaches the server finish-use event");check(backstabbed.merchants.Monolith.isPotion(h.getMainHandItem()),"Server main hand is refilled after real client consumption");
            Minecraft.getInstance().execute(()->{var mc=Minecraft.getInstance();mc.options.keyUse.setDown(false);clientHasPotion=backstabbed.merchants.Monolith.isPotion(mc.player.getMainHandItem());clientPotionCooldown=mc.player.getCooldowns().isOnCooldown(mc.player.getMainHandItem());System.out.println("CLIENT_POTION_HAND "+mc.player.getMainHandItem());});phase=63;ticks=0;
        }else if(phase==63&&++ticks>=5){check(clientHasPotion,"Real client main hand is refilled instead of displaying a glass bottle");check(clientPotionCooldown,"Refilled potion displays its active cooldown on the real client");check(clientChat.stream().anyMatch(t->t.contains("Monolith altar: SNEAK")),"Altar entry hint reaches the client chatbox");finish(null);
        }else if(phase==40&&++ticks>=80){
            cmd(s,"scoreboard players set $gamestate CmdData -2");cmd(s,"scoreboard players set $autostart GameRules 0");cmd(s,"scoreboard players set $start CmdData 0");cmd(s,"tag BackstabbedDev remove queued");cmd(s,"tag BackstabbedDev remove autoqueue");cmd(s,"tag BackstabbedDev add spectating");cmd(s,"tag BackstabbedDev remove MonolithParticipant");cmd(s,"gamemode spectator BackstabbedDev");cmd(s,"execute as BackstabbedDev run spectate");cmd(s,"tp BackstabbedDev 22.4 2 90 -90 0");phase=41;ticks=0;
        }else if(phase==41&&++ticks>=80){
            var h=s.getPlayerList().getPlayerByName("BackstabbedDev");results.add("Server camera "+h.position()+" yaw "+h.getYRot()+" pitch "+h.getXRot());picture("monolith-voting");phase=42;ticks=0;
        }else if(phase==42&&++ticks>=20){
            cmd(s,"scoreboard players set $gamestate CmdData 0");cmd(s,"function monolith:select");phase=48;ticks=0;
        }else if(phase==48&&++ticks>=60){
            cmd(s,"scoreboard players set $autostart GameRules 0");cmd(s,"scoreboard players set $start CmdData 0");
            var h=s.getPlayerList().getPlayerByName("BackstabbedDev");prepare(s,h);cmd(s,"scoreboard players set $gamestate CmdData 0");cmd(s,"tag BackstabbedDev add autoqueue");faceAltar(s,h,0);Minecraft.getInstance().execute(()->Minecraft.getInstance().options.keyShift.setDown(false));pictureIndex=0;phase=45;ticks=0;
        }else if(phase==45&&++ticks>=60){
            picture("monolith-view-"+pictureIndex);var h=s.getPlayerList().getPlayerByName("BackstabbedDev");h.teleportTo(s.overworld(),h.getX(),h.getY(),h.getZ(),java.util.Set.of(),h.getYRot(),55,false);phase=46;ticks=0;
        }else if(phase==46&&++ticks>=25){
            picture("monolith-altar-rune-"+pictureIndex);faceAltar(s,s.getPlayerList().getPlayerByName("BackstabbedDev"),pictureIndex);Minecraft.getInstance().execute(()->Minecraft.getInstance().options.keyShift.setDown(true));phase=43;ticks=0;
        }else if(phase==43){
            var h=s.getPlayerList().getPlayerByName("BackstabbedDev");h.setShiftKeyDown(true);
            if(++ticks>=60){picture("monolith-runes-"+pictureIndex);if(pictureIndex==0)picture("monolith-runes");phase=44;ticks=0;}
        }else if(phase==44&&++ticks>=20){
            Minecraft.getInstance().execute(()->Minecraft.getInstance().options.keyShift.setDown(false));s.getPlayerList().getPlayerByName("BackstabbedDev").setShiftKeyDown(false);
            if(++pictureIndex<3){faceAltar(s,s.getPlayerList().getPlayerByName("BackstabbedDev"),pictureIndex);phase=45;ticks=0;}
            else{check(clientChat.stream().anyMatch(t->t.contains("Look towards another altar")),"Sneak instruction reaches the client chatbox");phase=60;ticks=0;}
        }else if(phase==4&&++ticks>=65){picture("monolith-arena");cmd(s,"scoreboard players set $gamestate CmdData 0");cmd(s,"function monolith:reset");cmd(s,"execute positioned 28.0 2.0 89.0 as @e[type=marker,tag=MapVote,tag=Monolith,limit=1] run function mcm:lobby/voting/map_position_id");cmd(s,"tp BackstabbedDev 22.4 2 90 -90 0");phase=5;ticks=0;
        }else if(phase==5&&++ticks>=65){picture("monolith-voting");phase=6;ticks=0;
        }else if(phase==6&&++ticks>=20)finish(null);
    }catch(Throwable f){f.printStackTrace();finish(f);}}
    private void finish(Throwable f){phase=-1;try{var trace=new java.io.StringWriter();if(f!=null)f.printStackTrace(new java.io.PrintWriter(trace));Files.writeString(Path.of(System.getenv("ARENA_CHECK_DIR"),"results.txt"),(f==null?"PASS\n":"FAIL "+f+"\n"+trace)+String.join("\n",results));}catch(Exception e){e.printStackTrace();}Minecraft.getInstance().execute(()->Minecraft.getInstance().stop());}
}
