package gravity_changer.test;

import gravity_changer.api.GravityChangerAPI;
import net.minecraft.core.Direction;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.npc.Villager;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.AABB;
import net.minecraft.network.chat.Component;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;
import java.util.*;

@PrefixGameTestTemplate(false)
public final class KlutMobilityTests {
    private static final Map<UUID,List<Component>> HUD=new HashMap<>();
    private static final Vec3 MID=new Vec3(36895.5,11,36930.5);
    @GameTest(template="empty",templateNamespace="gravity_changer",batch="klut_boots",timeoutTicks=400)
    public static void realBootsAndInvertedElevators(GameTestHelper h) {
        if(!Boolean.getBoolean("backstabbed.boots")){h.succeed();return;}
        for(int x=2303;x<=2307;x++)for(int z=2303;z<=2309;z++)h.getLevel().getChunk(x,z);
        ServerPlayer a=player(h,"BootsA"),b=player(h,"BootsB");
        List<ServerPlayer> players=players(h);players.add(a);players.add(b);
        try {
            for(String s:List.of("CmdData","dead","klut_air","kh_owner","kh_cd","kh_seen","kh_was"))cmd(a,"scoreboard objectives add "+s+" dummy");
            cmd(a,"scoreboard players set $selectedMap CmdData 20");cmd(a,"scoreboard players set $gamestate CmdData 1");
            cmd(a,"function klut27_elevators:load");cmd(a,"function klut27:mobility/load");
            for(ServerPlayer p:List.of(a,b)){p.addTag("queued");p.setPos(MID);cmd(p,"scoreboard players set @s dead 0");cmd(p,"function klut27:mobility/cleanup");}
            if(Boolean.getBoolean("backstabbed.bootsStandalone"))cmd(a,"scoreboard objectives remove dead");
            b.setPos(MID.add(2,0,0));
            cmd(a,"function klut27:npc_reset");
            var npcs=h.getLevel().getEntitiesOfClass(Villager.class,new AABB(36848,-64,36848,36930,80,36950),e->e.getTags().contains("Klut27Engineer"));
            h.assertTrue(npcs.size()==1,"One engineer after reset");var npc=npcs.getFirst();
            h.assertTrue(npc.getName().getString().equals("Engineer"),"Merchant renamed in reset snapshot");
            var trades=npc.getOffers();h.assertTrue(trades.size()==2,"Toy gun and boots, no retired hook upgrade");
            var sale=trades.get(1);h.assertTrue(sale.getResult().is(Items.LEATHER_BOOTS),"Boots use vanilla leather item");
            h.assertTrue(!sale.satisfiedBy(new ItemStack(Items.NETHERITE_SCRAP,3),ItemStack.EMPTY),"Three scraps rejected");
            var payment=new ItemStack(Items.NETHERITE_SCRAP,7);
            h.assertTrue(sale.take(payment,ItemStack.EMPTY)&&payment.getCount()==3,"Exactly four scraps consumed");
            ItemStack boots=sale.assemble();
            h.assertTrue(boots.get(net.minecraft.core.component.DataComponents.DYED_COLOR).rgb()==3949738,"Boots dyed vanilla blue");
            a.getInventory().setItem(0,boots.copy());a.setPos(36895.5,-6,36930.5);tick(a);
            h.assertTrue(GravityChangerAPI.getGravityDirection(a)==Direction.DOWN,"Carried boots do not activate");
            a.setItemSlot(EquipmentSlot.FEET,boots.copy());a.setPos(36895.5,-5.99,36930.5);tick(a);
            h.assertTrue(GravityChangerAPI.getGravityDirection(a)==Direction.DOWN,"Above low threshold stays down");
            a.setPos(36895.5,-6,36930.5);tick(a);
            h.assertTrue(GravityChangerAPI.getGravityDirection(a)==Direction.UP&&score(a,"kb_cd")==300,"Exact Y=-6 flips immediately and starts 300 ticks: gravity="+GravityChangerAPI.getGravityDirection(a)+" base="+GravityChangerAPI.getBaseGravityDirection(a)+" cd="+score(a,"kb_cd")+" tags="+a.getTags()+" dim="+a.level().dimension().location()+" boots="+a.getItemBySlot(EquipmentSlot.FEET));
            h.assertTrue(a.hasEffect(MobEffects.SLOW_FALLING)&&a.getEffect(MobEffects.JUMP).getAmplifier()==2,"Slow falling I and jump boost III applied");
            a.setPos(36895.5,10,36930.5);for(int i=0;i<150;i++)tick(a);
            h.assertTrue(GravityChangerAPI.getGravityDirection(a)==Direction.UP&&score(a,"kb_cd")==150,"No early flip at high threshold during cooldown");
            cmd(a,"scoreboard players set @s e.cooldown 15");cmd(a,"function klut27:mobility/hud");
            String hud=last(a);h.assertTrue(hud.contains("重力靴 | ■■■■■————— | 7.5s")&&hud.contains("电梯 |"),"Combined HUD includes exact sample bar and both cooldowns: "+hud);
            boolean[] yellow={false},aqua={false};HUD.get(a.getUUID()).getLast().visit((style,text)->{if(style.getColor()!=null){yellow[0]|=style.getColor().getValue()==0xFFFF55;aqua[0]|=style.getColor().getValue()==0x55FFFF;}return Optional.empty();},net.minecraft.network.chat.Style.EMPTY);
            h.assertTrue(yellow[0]&&aqua[0],"Boots yellow and elevator light blue in actual actionbar packet");
            for(int i=0;i<149;i++)tick(a);
            h.assertTrue(score(a,"kb_cd")==1&&GravityChangerAPI.getGravityDirection(a)==Direction.UP,"Last cooldown tick still blocks");tick(a);
            h.assertTrue(score(a,"kb_cd")==300&&GravityChangerAPI.getGravityDirection(a)==Direction.DOWN,"Exact cooldown completion at Y=10 flips down");
            h.assertTrue(!a.hasEffect(MobEffects.SLOW_FALLING)&&!a.hasEffect(MobEffects.JUMP),"Down transition clears both effects");
            cmd(a,"scoreboard players set @s kb_cd 0");a.setPos(36895.5,-6,36930.5);tick(a);
            a.setItemSlot(EquipmentSlot.FEET,ItemStack.EMPTY);tick(a);
            h.assertTrue(GravityChangerAPI.getGravityDirection(a)==Direction.DOWN&&score(a,"kb_cd")==299,"Unequip safely restores down but preserves cooldown");
            a.setItemSlot(EquipmentSlot.FEET,boots.copy());tick(a);
            h.assertTrue(GravityChangerAPI.getGravityDirection(a)==Direction.DOWN&&score(a,"kb_cd")==298,"Re-equip cannot bypass cooldown");
            b.setItemSlot(EquipmentSlot.FEET,boots.copy());b.setPos(36897.5,-6,36930.5);tick(b);
            h.assertTrue(score(b,"kb_cd")==300&&score(a,"kb_cd")==298,"Two players have independent cooldowns");
            cmd(b,"function klut27:cleanup_player");h.assertTrue(GravityChangerAPI.getGravityDirection(b)==Direction.DOWN&&!b.hasEffect(MobEffects.JUMP),"Lifecycle cleanup removes effects and restores gravity");
            b.setItemSlot(EquipmentSlot.FEET,ItemStack.EMPTY);
            cmd(a,"function klut27:cleanup_player");
            a.setItemSlot(EquipmentSlot.FEET,ItemStack.EMPTY);
            cmd(a,"item replace entity @s hotbar.1 with warped_fungus_on_a_stick[custom_data={gun:1b}]");
            cmd(a,"item replace entity @s hotbar.0 with gravity_changer:grappling_hook[custom_data={klut27_hook:1b}]");a.addTag("Klut27Hook");
            cmd(a,"function klut27:give_hook");h.assertTrue(a.getInventory().getItem(0).isEmpty()&&a.getInventory().getItem(1).is(Items.WARPED_FUNGUS_ON_A_STICK),"Retired grant clears legacy hook without replacing gun");
            elevators(h,a,b);
            b.setItemSlot(EquipmentSlot.FEET,boots.copy());b.setPos(36897.5,-6,36930.5);tick(b);
            h.assertTrue(b.getTags().contains("KlutMobility")&&GravityChangerAPI.getGravityDirection(b)==Direction.UP,"Death fixture starts with active boots");
            b.setHealth(0);cmd(b,"function klut27:mobility/global_tick");
            h.assertTrue(!b.getTags().contains("KlutMobility")&&score(b,"kb_cd")==0&&GravityChangerAPI.getGravityDirection(b)==Direction.DOWN,"Actual death clears mobility state");
            System.out.println("KLUT BOOTS: thresholds, 300-tick cooldown, two players, native trade, cleanup and combined HUD passed; standalone="+Boolean.getBoolean("backstabbed.bootsStandalone"));
        } finally {for(ServerPlayer p:List.of(a,b)){players.remove(p);p.discard();}HUD.clear();}
        h.succeed();
    }
    private static void elevators(GameTestHelper h,ServerPlayer a,ServerPlayer b){
        cmd(a,"fill 36894 -3 36929 36896 24 36931 air");
        for(int y:new int[]{0,10,20})cmd(a,"setblock 36895 "+y+" 36930 white_shulker_box{lock:{components:{\"minecraft:custom_name\":\"\\\"5567353566-5331\\\"\"}}}");
        a.setPos(MID);b.setPos(MID.add(2,0,0));
        cmd(a,"function klut27:mobility/tick");h.assertTrue(last(a).contains("JUMP to go UP")&&last(a).contains("SNEAK to go DOWN"),"Middle floor shows both reachable directions");
        cmd(a,"scoreboard players set @s e.jumped 1");cmd(a,"function klut27:mobility/tick");
        h.assertTrue(Math.abs(a.getY()-21)<1e-5&&score(a,"e.cooldown")==30,"Down-gravity jump takes next upper stop with 1.5s cooldown");
        cmd(a,"scoreboard players set @s e.sneakedTime 1");cmd(a,"function klut27:mobility/tick");h.assertTrue(Math.abs(a.getY()-21)<1e-5,"Input blocked during lift cooldown");
        cmd(a,"scoreboard players set @s e.cooldown 1");cmd(a,"scoreboard players set @s e.sneakedTime 1");cmd(a,"function klut27:mobility/tick");h.assertTrue(Math.abs(a.getY()-11)<1e-5,"Lift available at exact cooldown expiry");
        cmd(a,"gravity set_base_direction up @s");
        a.setPos(MID.x,9.999998,MID.z);cmd(a,"scoreboard players set @s e.cooldown 0");cmd(a,"scoreboard players set @s ke_scan 0");
        cmd(a,"function klut27:mobility/tick");h.assertTrue(last(a).contains("JUMP to go UP")&&last(a).contains("SNEAK to go DOWN"),"Inverted player sees both directions from ceiling contact");
        cmd(a,"scoreboard players set @s e.jumped 1");cmd(a,"function klut27:mobility/tick");
        h.assertTrue(Math.abs(a.getY()-19.999998)<1e-5&&GravityChangerAPI.getGravityDirection(a)==Direction.UP&&h.getLevel().noCollision(a),"Inverted jump lands below upper platform without collision");
        cmd(a,"scoreboard players set @s e.cooldown 0");cmd(a,"scoreboard players set @s ke_scan 0");cmd(a,"function klut27:mobility/tick");
        h.assertTrue(!last(a).contains("JUMP")&&last(a).contains("SNEAK"),"Top stop only shows downward hint");
        cmd(a,"scoreboard players set @s e.sneakedTime 1");cmd(a,"function klut27:mobility/tick");h.assertTrue(Math.abs(a.getY()-9.999998)<1e-5,"Inverted sneak goes toward lower world Y");
        cmd(a,"setblock 36895 19 36930 stone");cmd(a,"scoreboard players set @s e.cooldown 0");cmd(a,"scoreboard players set @s ke_scan 0");cmd(a,"function klut27:mobility/tick");
        h.assertTrue(score(a,"ke_up")==0&&!last(a).contains("JUMP"),"Blocked inverted landing cannot be offered");
        cmd(a,"scoreboard players set @s e.jumped 1");cmd(a,"function klut27:mobility/tick");h.assertTrue(score(a,"e.cooldown")==0&&Math.abs(a.getY()-9.999998)<1e-5,"Unavailable destination neither teleports nor charges cooldown");
        cmd(a,"setblock 36895 19 36930 air");cmd(a,"setblock 36895 20 36930 black_wool");cmd(a,"scoreboard players set @s ke_scan 0");cmd(a,"function klut27:mobility/tick");h.assertTrue(score(a,"ke_up")==0,"Exploded black-wool elevator is not a destination");
        cmd(a,"setblock 36895 20 36930 white_shulker_box");
        a.setPos(MID.x,19.999998,MID.z);
        cmd(a,"item replace entity @s armor.feet with leather_boots[custom_data={klut27_boots:1b}]");
        a.addTag("KlutBootsEquipped");a.addTag("KlutBootsUp");
        cmd(a,"scoreboard players set @s kb_cd 1");tick(a);
        h.assertTrue(GravityChangerAPI.getGravityDirection(a)==Direction.DOWN&&h.getLevel().noCollision(a),"Equipped boots expire under ceiling without embedding player");
        cmd(a,"gravity set_base_direction up @s");a.setPos(MID.x,19.999998,MID.z);
        a.addTag("KlutBootsUp");a.setItemSlot(EquipmentSlot.FEET,ItemStack.EMPTY);tick(a);
        h.assertTrue(GravityChangerAPI.getGravityDirection(a)==Direction.DOWN&&h.getLevel().noCollision(a),"Unequipping under ceiling preserves a collision-free body volume");
        cmd(a,"function klut27:cleanup_player");
        System.out.println("KLUT ELEVATORS: down/up contacts, clearance, hints, cooldown and destroyed-stop checks passed");
    }
    private static void tick(ServerPlayer p){cmd(p,"function klut27:mobility/player");}
    private static String last(ServerPlayer p){return HUD.getOrDefault(p.getUUID(),List.of(Component.empty())).getLast().getString();}
    private static int score(Entity p,String name){var s=p.getServer().getScoreboard();return s.getOrCreatePlayerScore(p,s.getObjective(name)).get();}
    private static void cmd(Entity p,String text){p.getServer().getCommands().performPrefixedCommand(p.getServer().createCommandSourceStack().withEntity(p).withPosition(p.position()).withLevel((net.minecraft.server.level.ServerLevel)p.level()).withPermission(4).withSuppressedOutput(),text);GravityChangerAPI.getGravityComponent(p).tick();}
    private static ServerPlayer player(GameTestHelper h,String name){
        var profile=new com.mojang.authlib.GameProfile(UUID.randomUUID(),name);
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),profile,net.minecraft.server.level.ClientInformation.createDefault());
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p,net.minecraft.server.network.CommonListenerCookie.createInitial(profile,false)){
            @Override public void send(net.minecraft.network.protocol.Packet<?> packet){
                if(packet instanceof net.minecraft.network.protocol.game.ClientboundSetActionBarTextPacket bar)HUD.computeIfAbsent(p.getUUID(),k->new ArrayList<>()).add(bar.text());
            }
            @Override public void send(net.minecraft.network.protocol.Packet<?> packet,net.minecraft.network.PacketSendListener listener){send(packet);}
        };p.setClientLoaded(true);p.initInventoryMenu();h.getLevel().addNewPlayer(p);return p;
    }
    @SuppressWarnings("unchecked")private static List<ServerPlayer> players(GameTestHelper h){try{var f=net.minecraft.server.players.PlayerList.class.getDeclaredField("players");f.setAccessible(true);return(List<ServerPlayer>)f.get(h.getLevel().getServer().getPlayerList());}catch(Exception e){throw new RuntimeException(e);}}
}
