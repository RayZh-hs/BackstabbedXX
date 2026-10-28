package backstabbed.merchanttest;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.inventory.MerchantScreen;
import net.minecraft.core.component.DataComponents;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.inventory.MerchantMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

@Mod("backstabbed_merchant_test")
public final class MerchantRegression {
    private int phase, ticks;
    private int clientNpcId;
    private final List<String> results = new ArrayList<>();
    private volatile boolean clicked, shown;
    private Path output = Path.of(System.getenv("BACKSTABBED_MERCHANT_TEST_OUTPUT"));
    public MerchantRegression() { NeoForge.EVENT_BUS.addListener(this::tick); }
    private void cmd(MinecraftServer s, String c) {
        s.getCommands().performPrefixedCommand(s.createCommandSourceStack().withPermission(4).withSuppressedOutput(), c);
    }
    private void check(boolean ok, String label) {
        if (!ok) throw new AssertionError(label);
        results.add(label);
        System.out.println("MERCHANT PASS: " + label);
    }
    private Entity npc(MinecraftServer s, String tag) {
        return s.overworld().getAllEntities().iterator().hasNext()
            ? java.util.stream.StreamSupport.stream(s.overworld().getAllEntities().spliterator(), false)
                .filter(e -> e.isAlive() && e.getTags().contains(tag)).findFirst().orElseThrow() : null;
    }
    private long count(MinecraftServer s, String tag) {
        return java.util.stream.StreamSupport.stream(s.overworld().getAllEntities().spliterator(), false)
            .filter(e -> e.isAlive() && e.getTags().contains(tag)).count();
    }
    private void prepare(MinecraftServer s, ServerPlayer p, int map, Entity npc) {
        p.closeContainer();
        p.getInventory().clearContent();
        cmd(s, "scoreboard players set $gamestate CmdData 1");
        cmd(s, "scoreboard players set $selectedMap CmdData " + map);
        cmd(s, "tag " + p.getScoreboardName() + " add queued");
        cmd(s, "tag " + p.getScoreboardName() + " remove spectating");
        cmd(s, "scoreboard players set " + p.getScoreboardName() + " dead 0");
        cmd(s, "gamemode adventure " + p.getScoreboardName());
        p.teleportTo(s.overworld(), npc.getX() - 1.5, npc.getY(), npc.getZ() + 1.5, Set.of(), -135, 0, false);
    }
    private MerchantMenu open(ServerPlayer p, Entity npc) {
        NeoForge.EVENT_BUS.post(new PlayerInteractEvent.EntityInteract(p, InteractionHand.MAIN_HAND, npc));
        check(p.containerMenu instanceof MerchantMenu, npc.getType() + " opens a native MerchantMenu");
        return (MerchantMenu)p.containerMenu;
    }
    private int scraps(ServerPlayer p) { return p.getInventory().countItem(Items.NETHERITE_SCRAP); }
    private void economy(MinecraftServer s, ServerPlayer p, Entity npc, int map, boolean potion) {
        prepare(s, p, map, npc);
        check(!net.minecraft.world.entity.EntitySelector.pushableBy(p).test(npc),
            "players cannot push the merchant away from its shop and offer marker");
        var menu = open(p, npc);
        check(scraps(p) == 0 && p.getInventory().isEmpty(), "opening the menu spends and grants nothing");
        check(menu.getOffers().size() == 1 && menu.getOffers().getFirst().getCostA().getCount() == 4,
            "native offer costs exactly four scraps");
        menu.getSlot(0).set(new ItemStack(Items.NETHERITE_SCRAP, 3));
        menu.slotsChanged(p.getInventory());
        check(menu.getSlot(2).getItem().isEmpty(), "three scraps cannot purchase a result");
        p.closeContainer();
        check(scraps(p) == 3, "cancelling refunds all three inserted scraps");
        p.getInventory().clearContent();
        menu = open(p, npc);
        menu.getSlot(0).set(new ItemStack(Items.NETHERITE_SCRAP, 8));
        menu.slotsChanged(p.getInventory());
        var item = menu.getSlot(2).getItem();
        if (potion) {
            check(item.is(Items.POTION), "offer is a drinkable potion");
            var effects = item.get(DataComponents.POTION_CONTENTS).getAllEffects().iterator();
            var effect = effects.next();
            check(effect.getEffect().is(net.minecraft.world.effect.MobEffects.INVISIBILITY)
                && effect.getDuration() == 400 && effect.getAmplifier() == 0 && !effects.hasNext(),
                "potion contains only level-one invisibility for exactly 400 ticks (20 seconds)");
        } else {
            check(item.is(Items.STICK) && item.get(DataComponents.CUSTOM_DATA).copyTag().getBoolean("panda_toy_gun"),
                "toy offer preserves its non-firing panda_toy_gun identity");
            check(item.get(DataComponents.ITEM_MODEL).toString().equals("minecraft:role_items/gun"),
                "toy gun retains the real gun's appearance");
        }
        menu.quickMoveStack(p, 2);
        check(!p.getInventory().isEmpty() && menu.getSlot(0).getItem().getCount() == 4,
            "shift-clicking buys one item and consumes exactly four scraps");
        p.closeContainer();
        check(scraps(p) == 4, "closing returns the four unspent scraps");
        if (potion) {
            var purchased = p.getInventory().items.stream().filter(stack -> stack.is(Items.POTION)).findFirst().orElseThrow();
            purchased.finishUsingItem(p.level(), p);
            check(p.getEffect(net.minecraft.world.effect.MobEffects.INVISIBILITY).getDuration() == 400,
                "drinking the purchased potion applies exactly 20 seconds of invisibility");
            p.removeAllEffects();
        }
        p.getInventory().clearContent();
        for (int slot = 0; slot < 36; slot++) p.getInventory().setItem(slot, new ItemStack(Items.COBBLESTONE,64));
        menu = open(p,npc);
        menu.getSlot(0).set(new ItemStack(Items.NETHERITE_SCRAP,4));
        menu.slotsChanged(p.getInventory());
        check(menu.quickMoveStack(p,2).isEmpty() && menu.getSlot(0).getItem().getCount()==4,
            "a full inventory cannot consume scraps through a failed shift-click purchase");
        p.closeContainer();
        for (String guard : List.of("dead", "spectating", "spectator", "unqueued", "other_map", "inactive", "distance")) {
            prepare(s, p, map, npc);
            switch (guard) {
                case "dead" -> cmd(s, "scoreboard players set " + p.getScoreboardName() + " dead 1");
                case "spectating" -> p.addTag("spectating");
                case "spectator" -> cmd(s, "gamemode spectator " + p.getScoreboardName());
                case "unqueued" -> p.removeTag("queued");
                case "other_map" -> cmd(s, "scoreboard players set $selectedMap CmdData 2");
                case "inactive" -> cmd(s, "scoreboard players set $gamestate CmdData 0");
                case "distance" -> p.teleportTo(npc.getX() + 20, npc.getY(), npc.getZ());
            }
            NeoForge.EVENT_BUS.post(new PlayerInteractEvent.EntityInteract(p, InteractionHand.MAIN_HAND, npc));
            check(!(p.containerMenu instanceof MerchantMenu), "cannot open shop: " + guard);
        }
        prepare(s, p, map, npc);
        menu = open(p, npc);
        p.addTag("spectating");
        check(!menu.stillValid(p), "existing menu invalidates when the player becomes a spectator");
        prepare(s, p, map, npc);
        menu = open(p, npc);
        cmd(s, "scoreboard players set $gamestate CmdData 2");
        check(!menu.stillValid(p), "existing menu invalidates when the round ends");
        p.closeContainer();
    }
    private void tick(ServerTickEvent.Post event) {
        if (phase < 0) return;
        var s = event.getServer();
        try {
            var p = s.getPlayerList().getPlayerByName("BackstabbedDev");
            var dummy = p;
            if (p == null) return;
            if (phase == 0) {
                cmd(s,"difficulty normal");
                cmd(s,"scoreboard players set $selectedMap CmdData 19");
                cmd(s,"scoreboard players set $gamestate CmdData 0");
                cmd(s,"forceload add 32960 32448");
                p.teleportTo(s.overworld(),32961.5,48.0625,32462.5,Set.of(),-135,0,false);
                phase=1; ticks=0;
            } else if (phase==1 && ++ticks>=50) {
                cmd(s,"function underwater_base:activate");
                cmd(s,"function underwater_base:trader/spawn");
                check(count(s,"UnderwaterPotionTrader")==1 && count(s,"UnderwaterPotionOffers")==1,
                    "repeated underwater spawning creates exactly one zombie and offer marker");
                Entity zombie=npc(s,"UnderwaterPotionTrader");
                check(zombie.getType()==EntityType.ZOMBIE,"underwater trader is an actual zombie");
                check(p.level().getBlockState(zombie.blockPosition()).is(net.minecraft.world.level.block.Blocks.GRAY_CARPET),
                    "trader stands on the saved counter-room carpet");
                check(p.level().noCollision(zombie),"actual zombie collision box fits the existing room");
                economy(s,dummy,zombie,19,true);
                prepare(s,p,19,zombie);
                p.getInventory().add(new ItemStack(Items.NETHERITE_SCRAP,4));
                clientNpcId=zombie.getId();
                phase=2;ticks=0;clicked=false;shown=false;
            } else if ((phase==2 || phase==5) && ++ticks>=60) {
                var mc=Minecraft.getInstance();
                if(ticks==60) mc.execute(()->Screenshot.grab(output.getParent().toFile(),
                    phase==2?"underwater-trader.png":"panda-merchant.png",mc.getMainRenderTarget(),c->{}));
                if(ticks<70) return;
                if(!clicked) {
                    clicked=true;
                    mc.execute(()->{
                        // Entity tags are server-only; use this NPC's synchronized
                        // entity ID so nearby decorative pandas are not selected.
                        var target=mc.level.getEntity(clientNpcId);
                        if(target==null) throw new AssertionError("NPC not synchronized to client");
                        mc.gameMode.interact(mc.player,target,InteractionHand.MAIN_HAND);
                    });
                }
                if(ticks>=100) {
                    mc.execute(()->{shown=mc.screen instanceof MerchantScreen;
                        Screenshot.grab(output.getParent().toFile(),phase==2?"underwater-trade.png":"panda-trade.png",mc.getMainRenderTarget(),c->{});});
                }
                if(ticks>=110) {
                    check(shown,(phase==2?"zombie":"panda")+": real client right-click receives the vanilla MerchantScreen");
                    p.closeContainer();
                    if(phase==2) {
                        cmd(s,"function underwater_base:reset");
                        check(count(s,"UnderwaterPotionTrader")==0 && count(s,"UnderwaterPotionOffers")==0,
                            "underwater reset removes both NPC and offers");
                        cmd(s,"forceload add 8368 8368");
                        cmd(s,"scoreboard players set $selectedMap CmdData 13");
                        p.teleportTo(s.overworld(),8368.5,106,8375.5,Set.of(),-135,0,false);
                        phase=3;ticks=0;
                    } else { phase=6;ticks=0; }
                }
            } else if(phase==3 && ++ticks>=50) {
                cmd(s,"function panda_village:toy_shop/spawn");
                cmd(s,"function panda_village:toy_shop/spawn");
                check(count(s,"PandaToyShop")==2 && count(s,"PandaToyOffers")==1,
                    "repeated panda spawn creates only its panda and offer marker");
                Entity panda=java.util.stream.StreamSupport.stream(s.overworld().getAllEntities().spliterator(),false)
                    .filter(e->e.isAlive() && e.getType()==EntityType.PANDA && e.getTags().contains("PandaToyShop")).findFirst().orElseThrow();
                economy(s,dummy,panda,13,false);
                prepare(s,p,13,panda);
                p.getInventory().add(new ItemStack(Items.NETHERITE_SCRAP,4));
                clientNpcId=panda.getId();
                phase=5;ticks=0;clicked=false;shown=false;
            } else if(phase==6 && ++ticks>=10) {
                cmd(s,"function panda_village:reset");
                check(count(s,"PandaToyShop")==0 && count(s,"PandaToyOffers")==0,"panda reset removes both NPC and offers");
                finish(null);
            }
        } catch(Throwable failure) { failure.printStackTrace();finish(failure); }
    }
    private void finish(Throwable failure) {
        phase=-1;
        try { Files.writeString(output,(failure==null?"PASS\n":"FAIL: "+failure+"\n")+String.join("\n",results)+"\n"); }
        catch(Exception error) { error.printStackTrace(); }
        Minecraft.getInstance().execute(()->Minecraft.getInstance().stop());
    }
}
