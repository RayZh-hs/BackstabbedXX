package backstabbed.treehouse;

import java.util.Locale;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SimpleWaterloggedBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.level.material.Fluids;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Three inert visual backports for the unmodified source schematic. Both sides require this mod. */
@Mod("backstabbed_treehouse")
public final class TreehouseBlocks {
    // Keeping the original IDs lets the source retain its exact palette and rotations.
    private static final DeferredRegister.Blocks BLOCKS=DeferredRegister.createBlocks("minecraft");
    private static final DeferredRegister.Items ITEMS=DeferredRegister.createItems("minecraft");
    static {
        var shelf=BLOCKS.register("spruce_shelf",id->new Shelf(BlockBehaviour.Properties.ofFullCopy(Blocks.SPRUCE_PLANKS)
            .setId(ResourceKey.create(Registries.BLOCK,id)).noOcclusion()));
        var bush=BLOCKS.register("firefly_bush",id->new Plant(BlockBehaviour.Properties.ofFullCopy(Blocks.FERN)
            .setId(ResourceKey.create(Registries.BLOCK,id)).noCollission().noOcclusion().lightLevel(s->2)));
        var flower=BLOCKS.register("cactus_flower",id->new Plant(BlockBehaviour.Properties.ofFullCopy(Blocks.ALLIUM)
            .setId(ResourceKey.create(Registries.BLOCK,id)).noCollission().noOcclusion()));
        ITEMS.register("spruce_shelf",id->new BlockItem(shelf.get(),new Item.Properties().setId(ResourceKey.create(Registries.ITEM,id))));
        ITEMS.register("firefly_bush",id->new BlockItem(bush.get(),new Item.Properties().setId(ResourceKey.create(Registries.ITEM,id))));
        ITEMS.register("cactus_flower",id->new BlockItem(flower.get(),new Item.Properties().setId(ResourceKey.create(Registries.ITEM,id))));
    }
    public TreehouseBlocks(IEventBus bus){BLOCKS.register(bus);ITEMS.register(bus);}

    public static final class Plant extends Block {
        public static final MapCodec<Plant> CODEC=simpleCodec(Plant::new);
        public Plant(Properties properties){super(properties);}
        @Override protected MapCodec<? extends Block> codec(){return CODEC;}
        @Override protected VoxelShape getShape(BlockState s,BlockGetter l,BlockPos p,CollisionContext c){return Block.box(2,0,2,14,16,14);}
    }
    public enum Chain implements StringRepresentable {
        UNCONNECTED,LEFT,CENTER,RIGHT;
        public String getSerializedName(){return name().toLowerCase(Locale.ROOT);}
    }
    public static final class Shelf extends Block implements SimpleWaterloggedBlock {
        public static final MapCodec<Shelf> CODEC=simpleCodec(Shelf::new);
        public static final EnumProperty<Chain> CHAIN=EnumProperty.create("side_chain",Chain.class);
        public Shelf(Properties properties){super(properties);registerDefaultState(stateDefinition.any()
            .setValue(BlockStateProperties.HORIZONTAL_FACING,Direction.NORTH).setValue(BlockStateProperties.POWERED,false)
            .setValue(BlockStateProperties.WATERLOGGED,false).setValue(CHAIN,Chain.UNCONNECTED));}
        @Override protected MapCodec<? extends Block> codec(){return CODEC;}
        @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block,BlockState> b){
            b.add(BlockStateProperties.HORIZONTAL_FACING,BlockStateProperties.POWERED,BlockStateProperties.WATERLOGGED,CHAIN);
        }
        @Override public BlockState getStateForPlacement(BlockPlaceContext c){return defaultBlockState()
            .setValue(BlockStateProperties.HORIZONTAL_FACING,c.getHorizontalDirection().getOpposite())
            .setValue(BlockStateProperties.WATERLOGGED,c.getLevel().getFluidState(c.getClickedPos()).getType()==Fluids.WATER);}
        @Override protected FluidState getFluidState(BlockState s){return s.getValue(BlockStateProperties.WATERLOGGED)?Fluids.WATER.getSource(false):super.getFluidState(s);}
        @Override protected VoxelShape getShape(BlockState s,BlockGetter l,BlockPos p,CollisionContext c){
            return switch(s.getValue(BlockStateProperties.HORIZONTAL_FACING)){
                case NORTH->Shapes.or(box(0,0,13,16,16,16),box(0,0,11,16,4,13),box(0,12,11,16,16,13));
                case SOUTH->Shapes.or(box(0,0,0,16,16,3),box(0,0,3,16,4,5),box(0,12,3,16,16,5));
                case EAST->Shapes.or(box(0,0,0,3,16,16),box(3,0,0,5,4,16),box(3,12,0,5,16,16));
                case WEST->Shapes.or(box(13,0,0,16,16,16),box(11,0,0,13,4,16),box(11,12,0,13,16,16));
                default->Shapes.empty();
            };
        }
    }
}
