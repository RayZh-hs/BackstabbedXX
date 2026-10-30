package backstabbed.merchants;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtOps;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Marker;
import net.minecraft.world.entity.npc.Villager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.item.trading.MerchantOffers;
import net.minecraft.world.scores.ScoreHolder;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;

/** Opens vanilla merchant menus on the arena's actual panda/zombie NPCs.
 * Offers live in a nearby datapack marker, keeping prices/items in the map.
 * No custom entities, menus or network channels are registered on clients.
 */
@Mod("backstabbed_merchants")
public final class ArenaMerchants {
    public ArenaMerchants() {
        NeoForge.EVENT_BUS.addListener(this::interact);
        NeoForge.EVENT_BUS.addListener(ArenaSpawnGravity::register);
    }

    private static int score(Player player, ScoreHolder holder, String name, int fallback) {
        var board = player.getScoreboard();
        var objective = board.getObjective(name);
        var value = objective == null ? null : board.getPlayerScoreInfo(holder, objective);
        return value == null ? fallback : value.value();
    }

    private static boolean eligible(Player player, Entity npc, int map) {
        return npc.isAlive() && player.isAlive() && !player.isSpectator()
            && player.level() == npc.level() && player.distanceToSqr(npc) <= 25
            && player.getTags().contains("queued") && !player.getTags().contains("spectating")
            && score(player, player, "dead", 0) == 0
            && score(player, ScoreHolder.forNameOnly("$gamestate"), "CmdData", -1) == 1
            && score(player, ScoreHolder.forNameOnly("$selectedMap"), "CmdData", -1) == map;
    }

    private void interact(PlayerInteractEvent.EntityInteract event) {
        Entity npc = event.getTarget();
        int map;
        String offerTag;
        if (npc.getType() == EntityType.ZOMBIE && npc.getTags().contains("UnderwaterPotionTrader")) {
            map = 19;
            offerTag = "UnderwaterPotionOffers";
        } else if (npc.getType() == EntityType.PANDA && npc.getTags().contains("PandaToyShop")) {
            map = 13;
            offerTag = "PandaToyOffers";
        } else {
            return;
        }
        // Suppress feeding, spawn eggs and all other vanilla NPC interactions.
        event.setCanceled(true);
        event.setCancellationResult(InteractionResult.SUCCESS);
        if (event.getHand() != InteractionHand.MAIN_HAND
                || !(event.getEntity() instanceof ServerPlayer player)
                || !eligible(player, npc, map)) return;
        var markers = npc.level().getEntitiesOfClass(Marker.class, npc.getBoundingBox().inflate(1),
            marker -> marker.getTags().contains(offerTag));
        if (markers.size() != 1) return;
        var marker = markers.getFirst();
        CompoundTag data = marker.saveWithoutId(new CompoundTag()).getCompound("data");
        if (!data.contains("offers")) return;
        var offers = MerchantOffers.CODEC.parse(npc.registryAccess().createSerializationContext(NbtOps.INSTANCE),
            data.get("offers")).result();
        if (offers.isEmpty() || offers.get().isEmpty()) return;
        // Each viewer gets an independent session. Vanilla handles payment,
        // result slots, shift-clicking, full inventories and returned inputs.
        player.closeContainer();
        var merchant = new Session(player, npc, marker, map, offers.get());
        merchant.openTradingScreen(player, npc.getDisplayName(), 1);
    }

    // Vanilla's shift-click sound path expects the Merchant to also be an
    // Entity. This private, unspawned villager supplies that contract without
    // adding a hidden villager, hitbox, ticking mob or client entity type.
    private static final class Session extends Villager {
        private final Entity npc;
        private final Marker marker;
        private final int map;
        private Player customer;
        private MerchantOffers offers;

        Session(Player customer, Entity npc, Marker marker, int map, MerchantOffers offers) {
            super(EntityType.VILLAGER, npc.level());
            setPos(npc.position());
            this.customer = customer;
            this.npc = npc;
            this.marker = marker;
            this.map = map;
            this.offers = offers;
        }

        @Override public void setTradingPlayer(Player player) { customer = player; }
        @Override public Player getTradingPlayer() { return customer; }
        @Override public MerchantOffers getOffers() { return offers; }
        @Override public void overrideOffers(MerchantOffers value) { offers = value; }
        @Override public void notifyTrade(MerchantOffer offer) {
            offer.increaseUses();
            npc.playSound(SoundEvents.VILLAGER_YES, 0.7f, 1.2f);
        }
        @Override public void notifyTradeUpdated(ItemStack stack) {}
        @Override public int getVillagerXp() { return 0; }
        @Override public void overrideXp(int xp) {}
        @Override public boolean showProgressBar() { return false; }
        @Override public boolean canRestock() { return false; }
        @Override public SoundEvent getNotifyTradeSound() { return SoundEvents.VILLAGER_YES; }
        @Override public boolean isClientSide() { return false; }
        @Override public boolean stillValid(Player player) {
            return customer == player && marker.isAlive() && eligible(player, npc, map);
        }
    }
}
