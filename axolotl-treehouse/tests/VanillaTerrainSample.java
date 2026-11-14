package backstabbed.regression;
import java.nio.file.*;
import net.minecraft.client.Minecraft;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.levelgen.Heightmap;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
@Mod("backstabbed_regression")
public class VanillaTerrainSample {
 int phase=0,index=0,chunk=0;double best=-1e9;int bx=0,bz=0;
 public VanillaTerrainSample(){NeoForge.EVENT_BUS.addListener(this::tick);}
 int height(MinecraftServer s,int x,int z){var l=s.overworld();return l.getChunkSource().getGenerator().getBaseHeight(x,z,Heightmap.Types.WORLD_SURFACE_WG,l,l.getChunkSource().randomState());}
 void tick(ServerTickEvent.Post e){var s=e.getServer();if(phase<0||s.getPlayerList().getPlayers().isEmpty())return;
 try{
  for(var p:s.getPlayerList().getPlayers())p.setGameMode(GameType.SPECTATOR);
  s.getCommands().performPrefixedCommand(s.createCommandSourceStack().withSuppressedOutput(),"scoreboard players set $gamestate CmdData -2");
  if(phase==0&&index==0&&Files.exists(Path.of(System.getenv("ARENA_CHECK_DIR"),"selection.json"))){var j=com.google.gson.JsonParser.parseString(Files.readString(Path.of(System.getenv("ARENA_CHECK_DIR"),"selection.json"))).getAsJsonObject();bx=j.getAsJsonArray("center").get(0).getAsInt();bz=j.getAsJsonArray("center").get(1).getAsInt();phase=1;}
  if(phase==0){
   for(int n=0;n<18&&index<625;n++,index++){
    int x=-384+(index%25)*32,z=-384+(index/25)*32,h=height(s,x,z);if(h>70)continue;
    double sum=0,min=400,inner=0;
    for(int i=0;i<12;i++){
     double a=i*Math.PI/6;int peak=0;
     for(int r:new int[]{144,192,240})peak=Math.max(peak,height(s,x+(int)(Math.cos(a)*r),z+(int)(Math.sin(a)*r)));
     sum+=peak;min=Math.min(min,peak);inner+=Math.max(0,height(s,x+(int)(Math.cos(a)*90),z+(int)(Math.sin(a)*90))-65);
    }
    double score=min*2+sum/12-inner/5-Math.abs(h-63)*3;
    if(score>best){best=score;bx=x;bz=z;System.out.println("VANILLA_CANDIDATE "+x+" "+z+" center="+h+" min="+min+" average="+sum/12+" score="+score);}
   }
   if(index>=625){Files.writeString(Path.of(System.getenv("ARENA_CHECK_DIR"),"selection.json"),"{\"seed\":"+s.overworld().getSeed()+",\"center\":["+bx+","+bz+"],\"size\":512,\"score\":"+best+"}");phase=1;}
  }else if(phase==1){
   for(int n=0;n<3&&chunk<1024;n++,chunk++){int cx=bx/16-16+chunk%32,cz=bz/16-16+chunk/32;s.overworld().getChunk(cx,cz);}
   if(chunk%48<3)System.out.println("VANILLA_CHUNKS "+chunk+"/1024");
   if(chunk>=1024){phase=-1;Files.writeString(Path.of(System.getenv("ARENA_CHECK_DIR"),"results.txt"),"PASS\nGenerated 1024 normal Minecraft 1.21.4 chunks\n");Minecraft.getInstance().execute(()->Minecraft.getInstance().stop());}
  }
 }catch(Throwable f){phase=-1;f.printStackTrace();try{Files.writeString(Path.of(System.getenv("ARENA_CHECK_DIR"),"results.txt"),"FAIL "+f);}catch(Exception ignored){}Minecraft.getInstance().execute(()->Minecraft.getInstance().stop());}}
}
