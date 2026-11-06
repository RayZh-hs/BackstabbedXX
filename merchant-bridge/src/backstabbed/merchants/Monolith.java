package backstabbed.merchants;

import java.util.*;
import net.minecraft.commands.Commands;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.TagParser;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.scores.ScoreHolder;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.living.LivingEntityUseItemEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;

/** Server-only summit targeting and reusable potion; all world policy remains in the arena datapack. */
public final class Monolith {
    private static final ResourceLocation COOLDOWN = ResourceLocation.parse("monolith:float");
    private static final String FLOAT_END = "MonolithFloatUntil", CD_END = "MonolithCooldownUntil";
    private static final Map<UUID, Selection> selections = new HashMap<>();
    private static final Map<UUID, Integer> refillSync = new HashMap<>();
    private static final Map<UUID, Integer> altarVisits = new HashMap<>();
    private record Selection(int source, List<Integer> ghosts) {}
    private static final String[] NAMES = {"Canopy", "Conifer", "Cherry"};
    private static final int[] COLORS = {0xFFE394, 0x64E8D0, 0xF6ADD4};
    private Monolith() {}
    public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("monolith").requires(s -> s.hasPermission(2))
            .then(Commands.literal("tick").executes(c -> { tick(c.getSource().getServer()); return 1; }))
            .then(Commands.literal("cleanup").executes(c -> {
                for (var p : c.getSource().getServer().getPlayerList().getPlayers()) cleanup(p);
                return 1;
            })));
    }
    public static void stopped(ServerStoppedEvent event) { selections.clear(); refillSync.clear(); altarVisits.clear(); }
    private static int score(ServerPlayer p, String holder, String name, int fallback) {
        var board=p.getScoreboard(); var objective=board.getObjective(name);
        var value=objective==null?null:board.getPlayerScoreInfo(ScoreHolder.forNameOnly(holder),objective);
        return value==null?fallback:value.value();
    }
    public static boolean eligible(ServerPlayer p) {
        int state=score(p,"$gamestate","CmdData",-1);
        return p.isAlive() && !p.isSpectator() && p.level().dimension()==net.minecraft.world.level.Level.OVERWORLD
            && p.getTags().contains("queued") && p.getTags().contains("MonolithParticipant")
            && !p.getTags().contains("spectating") && score(p,p.getScoreboardName(),"dead",0)==0
            && score(p,"$selectedMap","CmdData",-1)==24 && (state==0 || state==1);
    }
    public static boolean isPotion(ItemStack item) {
        var data=item.get(DataComponents.CUSTOM_DATA);
        return item.is(Items.POTION) && data!=null && data.copyTag().getBoolean("monolith_float");
    }
    public static void rightClick(PlayerInteractEvent.RightClickItem event) {
        if (!(event.getEntity() instanceof ServerPlayer p) || !isPotion(event.getItemStack())) return;
        long remaining=p.getPersistentData().getLong(CD_END)-p.serverLevel().getGameTime();
        if (!eligible(p) || score(p,"$gamestate","CmdData",-1)!=1 || remaining>0) {
            event.setCanceled(true);
            if (remaining>0) p.displayClientMessage(Component.literal("Float ready in "+((remaining+19)/20)+"s").withColor(0xFFE394),true);
        }
    }
    public static void consumed(LivingEntityUseItemEvent.Finish event) {
        if (!(event.getEntity() instanceof ServerPlayer p) || !isPotion(event.getItem())) return;
        // Vanilla has applied exactly 100 ticks of levitation. Return the original tagged potion, not a bottle.
        event.setResultStack(event.getItem().copyWithCount(1));
        long now=p.serverLevel().getGameTime();
        if (!eligible(p) || score(p,"$gamestate","CmdData",-1)!=1 || p.getPersistentData().getLong(CD_END)>now) {
            p.removeEffect(MobEffects.LEVITATION); return;
        }
        p.getPersistentData().putLong(FLOAT_END,now+100);
        p.getPersistentData().putLong(CD_END,now+600);
        p.getCooldowns().addCooldown(COOLDOWN,600);
        // The server returns the same potion, so ordinary slot diffing sees no
        // change. The vanilla client has predicted a glass bottle independently.
        // Send authoritative inventory state after its use animation finishes.
        refillSync.put(p.getUUID(),p.getServer().getTickCount()+2);
    }
    private static void removeGhosts(ServerPlayer p) {
        var old=selections.remove(p.getUUID());
        if (old!=null && !old.ghosts().isEmpty()) p.connection.send(new ClientboundRemoveEntitiesPacket(old.ghosts().stream().mapToInt(Integer::intValue).toArray()));
        if (old!=null && score(p,"$darkness","GameRules",0)!=1) p.removeEffect(MobEffects.DARKNESS);
    }
    public static void cleanup(ServerPlayer p) {
        removeGhosts(p);
        var data=p.getPersistentData();
        if (data.contains(FLOAT_END)) p.removeEffect(MobEffects.LEVITATION);
        data.remove(FLOAT_END); data.remove(CD_END);
        p.getCooldowns().removeCooldown(COOLDOWN);
        for(int i=0;i<p.getInventory().getContainerSize();i++) if(isPotion(p.getInventory().getItem(i)))p.getInventory().setItem(i,ItemStack.EMPTY);
        p.removeTag("MonolithEquipped");
        refillSync.remove(p.getUUID()); altarVisits.remove(p.getUUID());
    }
    private static List<Marker> altars(ServerLevel level) {
        var out=new ArrayList<Marker>();
        for(var e:level.getAllEntities())if(e instanceof Marker m && e.getTags().contains("MonolithAltar"))out.add(m);
        out.sort(Comparator.comparingInt(Monolith::altarId));return out;
    }
    private static int altarId(Marker altar) {
        for(int i=0;i<3;i++)if(altar.getTags().contains("MonolithAltar"+i))return i;
        return 3;
    }
    public static Vec3 runeCenter(Marker altar) {
        var data=altar.saveWithoutId(new CompoundTag()).getCompound("data");
        return data.contains("rune_x")?new Vec3(data.getDouble("rune_x"),data.getDouble("rune_y"),data.getDouble("rune_z")):altar.position().add(0,10,0);
    }
    public static Vec3 targetCenter(Marker altar) {
        var data=altar.saveWithoutId(new CompoundTag()).getCompound("data");
        return data.contains("target_x")?new Vec3(data.getDouble("target_x"),data.getDouble("target_y"),data.getDouble("target_z")):runeCenter(altar).add(0,3,0);
    }
    public static int source(ServerPlayer p,List<Marker> altars) {
        if(!p.onGround())return -1;
        for(int i=0;i<altars.size();i++) {var v=altars.get(i).position();if(Math.abs(p.getY()-v.y)<.8 && Math.hypot(p.getX()-v.x,p.getZ()-v.z)<=2.8)return i;}
        return -1;
    }
    public static int target(Vec3 eye,Vec3 look,List<Marker> altars,int source) {
        double best=Math.cos(Math.toRadians(9));int chosen=-1;
        for(int i=0;i<altars.size();i++)if(i!=source){double dot=look.dot(targetCenter(altars.get(i)).subtract(eye).normalize());if(dot>best){best=dot;chosen=i;}}
        return chosen;
    }
    private static int ghost(ServerPlayer p,Marker altar,int index) {
        try {
            var d=new Display.TextDisplay(EntityType.TEXT_DISPLAY,p.level());
            String color=String.format("#%06X",COLORS[index]);
            String text="{\"text\":\"    ✦    \\n ◇     ◇ \\n✧       ✧\\n⊕   ✦   ⊕\\n✧       ✧\\n ◇     ◇ \\n    ✦    \",\"color\":\""+color+"\",\"bold\":true}";
            CompoundTag tag=TagParser.parseTag("{billboard:\"center\",brightness:{sky:15,block:15},background:0,text_opacity:-1b,see_through:1b,shadow:1b,alignment:\"center\",line_width:200,view_range:4f,transformation:{translation:[0f,0f,0f],scale:[3f,3f,3f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]}}");
            tag.putString("text",text);
            // Darkness fog obscures distant emissive entities too. Project private runes
            // four metres along the true destination sightline, preserving angular scale.
            float scale=(float)(18/p.getEyePosition().distanceTo(targetCenter(altar)));
            var transform=tag.getCompound("transformation");
            var scales=new net.minecraft.nbt.ListTag();for(int k=0;k<3;k++)scales.add(net.minecraft.nbt.FloatTag.valueOf(scale));transform.put("scale",scales);
            d.load(tag); d.setPos(project(p,altar));
            p.connection.send(new ClientboundAddEntityPacket(d.getId(),d.getUUID(),d.getX(),d.getY(),d.getZ(),0,0,d.getType(),0,Vec3.ZERO,0));
            var values=d.getEntityData().getNonDefaultValues();if(values!=null)p.connection.send(new ClientboundSetEntityDataPacket(d.getId(),values));
            return d.getId();
        }catch(Exception e){throw new IllegalStateException("Monolith rune display",e);}
    }
    private static Vec3 project(ServerPlayer p,Marker altar) {
        var eye=p.getEyePosition();return eye.add(targetCenter(altar).subtract(eye).normalize().scale(4));
    }
    private static void rune(ServerPlayer p,Marker altar,int color) {
        var eye=p.getEyePosition();var destination=targetCenter(altar);var direction=destination.subtract(eye).normalize();
        var center=project(p,altar);double radius=18/eye.distanceTo(destination);
        var right=direction.cross(new Vec3(0,1,0)).normalize();var up=right.cross(direction).normalize();
        var dust=new DustParticleOptions(color,.2f);
        for(int i=0;i<28;i++){double a=i*Math.PI*2/28;var v=center.add(right.scale(Math.cos(a)*radius)).add(up.scale(Math.sin(a)*radius));
            p.serverLevel().sendParticles(p,dust,true,false,v.x,v.y,v.z,1,0,0,0,0);}
    }
    public static boolean travel(ServerPlayer p,Marker target) {
        Vec3 to=target.position();
        if(!p.serverLevel().noCollision(p,p.getBoundingBox().move(to.subtract(p.position()))) || !p.serverLevel().getBlockCollisions(p,p.getBoundingBox().move(to.subtract(p.position())).move(0,-.05,0)).iterator().hasNext())return false;
        var from=p.position().add(0,1,0);var end=to.add(0,1,0);
        for(int i=0;i<=120;i++){double t=i/120.;var v=from.lerp(end,t).add(0,Math.sin(t*Math.PI)*8,0);
            p.serverLevel().sendParticles(ParticleTypes.END_ROD,true,false,v.x,v.y,v.z,2,.025,.025,.025,.001);}
        var eyes=to.add(0,p.getEyeHeight(),0);var look=Vec3.ZERO;
        for(var other:altars(p.serverLevel()))if(other!=target)look=look.add(targetCenter(other).subtract(eyes).normalize());
        if(look.lengthSqr()<.01)look=p.getLookAngle();else look=look.normalize();
        float yaw=(float)Math.toDegrees(Math.atan2(-look.x,look.z));float pitch=(float)-Math.toDegrees(Math.asin(look.y));
        p.teleportTo(p.serverLevel(),to.x,to.y,to.z,Set.of(),yaw,pitch,false);p.setDeltaMovement(Vec3.ZERO);p.fallDistance=0;
        p.serverLevel().sendParticles(ParticleTypes.FLASH,to.x,to.y+1,to.z,1,0,0,0,0);
        p.playNotifySound(net.minecraft.sounds.SoundEvents.ENDERMAN_TELEPORT,net.minecraft.sounds.SoundSource.PLAYERS,.7f,1.4f);
        return true;
    }
    private static void syncPotion(ServerPlayer p) {
        for(int i=0;i<p.getInventory().getContainerSize();i++)if(isPotion(p.getInventory().getItem(i)))
            p.connection.send(new ClientboundSetPlayerInventoryPacket(i,p.getInventory().getItem(i).copy()));
    }
    private static void altarParticles(ServerLevel level,Marker altar,int color,long now) {
        var center=altar.position().add(0,.12,0);var dust=new DustParticleOptions(color,.7f);
        var tile=altar.saveWithoutId(new CompoundTag()).getCompound("data");
        var right=new Vec3(tile.getDouble("rune_right_x"),0,tile.getDouble("rune_right_z"));
        if(right.lengthSqr()<.5)right=altarId(altar)==1?new Vec3(0,0,1):new Vec3(1,0,0);
        var rune=runeCenter(altar);
        // The summit's upright stone circle also gets a visible inner outline.
        for(int i=0;i<40;i++){double a=i*Math.PI*2/40;var v=rune.add(right.scale(Math.cos(a)*6.3)).add(0,Math.sin(a)*6.3,0);
            level.sendParticles(dust,true,false,v.x,v.y,v.z,1,0,0,0,0);}
        // A persistent ring with two interlocking triangles marks the walkable altar.
        for(int i=0;i<36;i++){double a=i*Math.PI*2/36;var v=center.add(Math.cos(a)*1.8,0,Math.sin(a)*1.8);
            level.sendParticles(dust,true,false,v.x,v.y,v.z,1,0,0,0,0);}
        for(int triangle=0;triangle<2;triangle++)for(int side=0;side<3;side++){
            double a=(side*2+triangle)*Math.PI/3,b=(side*2+triangle+2)*Math.PI/3;
            var from=center.add(Math.cos(a)*1.55,0,Math.sin(a)*1.55);var to=center.add(Math.cos(b)*1.55,0,Math.sin(b)*1.55);
            for(int step=0;step<6;step++){var v=from.lerp(to,step/6.);level.sendParticles(dust,true,false,v.x,v.y,v.z,1,0,0,0,0);}
        }
        // Enchanting-table glyphs curl inward above the rune without requiring sneak.
        for(int i=0;i<4;i++){double a=(now*.045)+i*Math.PI/2;
            level.sendParticles(ParticleTypes.ENCHANT,true,false,center.x,center.y+1.1,center.z,0,Math.cos(a)*2.2,1.5,Math.sin(a)*2.2,1);}
    }
    private static void tick(net.minecraft.server.MinecraftServer server) {
        var altars=altars(server.overworld());
        if(altars.size()==3 && server.getTickCount()%6==0) {
            var sample=server.getPlayerList().getPlayers().stream().findFirst();
            if(sample.isPresent() && score(sample.get(),"$selectedMap","CmdData",-1)==24
                && score(sample.get(),"$gamestate","CmdData",-1)>=0 && score(sample.get(),"$gamestate","CmdData",-1)<=1)
                for(int i=0;i<3;i++)altarParticles(server.overworld(),altars.get(i),COLORS[i],server.overworld().getGameTime());
        }
        for(var p:server.getPlayerList().getPlayers()) {
            if(!eligible(p)) {if(p.getTags().contains("MonolithEquipped")||selections.containsKey(p.getUUID())||altarVisits.containsKey(p.getUUID())||refillSync.containsKey(p.getUUID())||p.getPersistentData().contains(CD_END))cleanup(p);continue;}
            long now=p.serverLevel().getGameTime();var data=p.getPersistentData();
            if(data.contains(FLOAT_END) && (now>=data.getLong(FLOAT_END) || (p.isShiftKeyDown()&&!p.onGround()))) {p.removeEffect(MobEffects.LEVITATION);data.remove(FLOAT_END);}
            long remaining=data.getLong(CD_END)-now;
            var syncAt=refillSync.get(p.getUUID());
            if(syncAt!=null && server.getTickCount()>=syncAt){p.inventoryMenu.broadcastFullState();syncPotion(p);refillSync.remove(p.getUUID());}
            if(remaining>0 && server.getTickCount()%20==0)syncPotion(p);
            if(remaining>0 && !p.getCooldowns().isOnCooldown(potionInInventory(p)))p.getCooldowns().addCooldown(COOLDOWN,(int)remaining);
            var old=selections.get(p.getUUID());int source=source(p,altars);
            int previous=altarVisits.getOrDefault(p.getUUID(),-1);
            if(source!=previous){altarVisits.put(p.getUUID(),source);if(source>=0)
                p.sendSystemMessage(Component.literal("Monolith altar: SNEAK here to reveal the other altars and travel.").withColor(COLORS[source]));}
            if(old!=null && (!p.isShiftKeyDown()||source!=old.source())) {
                int aimed=target(p.getEyePosition(),p.getLookAngle(),altars,old.source());
                boolean release=!p.isShiftKeyDown()&&source==old.source();removeGhosts(p);
                if(release&&aimed>=0)travel(p,altars.get(aimed));
            }
            if(p.isShiftKeyDown() && source>=0 && altars.size()==3) {
                if(!selections.containsKey(p.getUUID())) {var ids=new ArrayList<Integer>();for(int i=0;i<3;i++)if(i!=source)ids.add(ghost(p,altars.get(i),i));selections.put(p.getUUID(),new Selection(source,ids));
                    p.sendSystemMessage(Component.literal("Look towards another altar's glowing rune while holding SNEAK. Release SNEAK to travel to it.").withColor(0xD9FFF5));}
                var selected=selections.get(p.getUUID());int ghostIndex=0;
                for(int i=0;i<3;i++)if(i!=source)p.connection.send(ClientboundTeleportEntityPacket.teleport(selected.ghosts().get(ghostIndex++),new PositionMoveRotation(project(p,altars.get(i)),Vec3.ZERO,0,0),Set.of(),false));
                p.addEffect(new MobEffectInstance(MobEffects.DARKNESS,40,0,false,false));
                int aimed=target(p.getEyePosition(),p.getLookAngle(),altars,source);
                if(now%4==0)for(int i=0;i<3;i++)if(i!=source)rune(p,altars.get(i),aimed==i?0xFFFFFF:COLORS[i]);
                p.displayClientMessage(Component.literal(aimed<0?"Aim at a rune · release sneak to travel":NAMES[aimed]+" · release sneak to travel").withColor(aimed<0?0xAAAAAA:COLORS[aimed]),true);
            } else if(remaining>0) p.displayClientMessage(Component.literal("Float · "+((remaining+19)/20)+"s").withColor(0xFFE394),true);
        }
        selections.keySet().removeIf(id->server.getPlayerList().getPlayer(id)==null);
        refillSync.keySet().removeIf(id->server.getPlayerList().getPlayer(id)==null);
        altarVisits.keySet().removeIf(id->server.getPlayerList().getPlayer(id)==null);
    }
    private static ItemStack potionInInventory(ServerPlayer p) {
        for(int i=0;i<p.getInventory().getContainerSize();i++)if(isPotion(p.getInventory().getItem(i)))return p.getInventory().getItem(i);
        return ItemStack.EMPTY;
    }
}
