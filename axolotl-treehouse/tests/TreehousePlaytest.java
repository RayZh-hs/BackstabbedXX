package backstabbed.regression;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.GameType;
import net.minecraft.world.scores.ScoreHolder;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.bus.api.EventPriority;

@Mod("backstabbed_regression")
public final class TreehousePlaytest {
 private int phase=0,ticks=0;private volatile boolean scenicChunksReady;private final List<String>results=new ArrayList<>();
 public TreehousePlaytest(){NeoForge.EVENT_BUS.addListener(EventPriority.LOWEST,this::tick);}
 private void cmd(MinecraftServer s,String c){s.getCommands().performPrefixedCommand(s.createCommandSourceStack().withPermission(4).withSuppressedOutput(),c);}
 private int score(MinecraftServer s,String h,String o){var v=s.getScoreboard().getPlayerScoreInfo(ScoreHolder.forNameOnly(h),s.getScoreboard().getObjective(o));return v==null?0:v.value();}
 private void check(boolean ok,String m){if(!ok)throw new AssertionError(m);results.add(m);System.out.println("TREEHOUSE_CHECK "+m);}
 private List<Entity>tagged(MinecraftServer s,String tag){var out=new ArrayList<Entity>();for(var e:s.overworld().getAllEntities())if(e.getTags().contains(tag))out.add(e);return out;}
 private void prepare(MinecraftServer s,ServerPlayer p){p.setGameMode(GameType.ADVENTURE);p.setDeltaMovement(0,0,0);p.fallDistance=0;String n=p.getScoreboardName();cmd(s,"spectate "+n);cmd(s,"tag "+n+" add queued");cmd(s,"tag "+n+" remove spectating");cmd(s,"scoreboard players set "+n+" dead 0");cmd(s,"scoreboard players set $selectedMap CmdData 25");cmd(s,"scoreboard players set $gamestate CmdData 1");cmd(s,"scoreboard players set $graceperiod CmdData 0");p.addTag("AxolotlTreehouseParticipant");}
 private void probe(MinecraftServer s,ServerPlayer p,double x,double y,double z){p.teleportTo(x,y,z);p.setDeltaMovement(0,0,0);p.fallDistance=0;cmd(s,"function axolotl_treehouse:functionality");}
 private void picture(String name){Minecraft.getInstance().execute(()->{var m=Minecraft.getInstance();try{Files.writeString(Path.of(System.getenv("ARENA_CHECK_DIR"),name+"-camera.txt"),m.player.position()+" yaw="+m.player.getYRot()+" pitch="+m.player.getXRot()+" camera="+m.getCameraEntity().position());}catch(Exception e){throw new RuntimeException(e);}Screenshot.grab(Path.of(System.getenv("ARENA_CHECK_DIR")).toFile(),name+".png",m.getMainRenderTarget(),x->{});});}
 private void views(MinecraftServer s){cmd(s,"time set 6000");cmd(s,"weather clear");cmd(s,"tag BackstabbedDev remove queued");cmd(s,"tag BackstabbedDev remove autoqueue");cmd(s,"tag BackstabbedDev add spectating");cmd(s,"gamemode spectator BackstabbedDev");cmd(s,"scoreboard players set $gamestate CmdData -2");cmd(s,"tp BackstabbedDev 57512 116 57645 -117 19");Minecraft.getInstance().execute(()->{var m=Minecraft.getInstance();m.options.hideGui=true;for(var key:List.of(m.options.keyUp,m.options.keyDown,m.options.keyLeft,m.options.keyRight,m.options.keyJump,m.options.keyShift))key.setDown(false);});phase=4;ticks=0;}
 private void tick(ServerTickEvent.Post event){if(phase<0)return;var s=event.getServer();var p=s.getPlayerList().getPlayerByName("PlaytestDummy1");if(p==null||s.getPlayerList().getPlayerCount()!=4)return;try{
  if(phase==0&&++ticks>=80){
   for(String id:Files.readAllLines(Path.of(System.getenv("ARENA_CHECK_DIR"),"functions.txt")))check(s.getFunctions().get(ResourceLocation.parse(id)).isPresent(),"Parsed "+id);
   for(String id:List.of("spruce_shelf","firefly_bush","cactus_flower"))check(BuiltInRegistries.BLOCK.getValue(ResourceLocation.parse("minecraft:"+id))!=net.minecraft.world.level.block.Blocks.AIR,"Registered original minecraft:"+id);
   cmd(s,"scoreboard players set $autostart GameRules 0");cmd(s,"scoreboard players set $gamestate CmdData 0");cmd(s,"function axolotl_treehouse:select");phase=1;ticks=0;
  }else if(phase==1&&++ticks>=100){
   if(System.getenv("TREEHOUSE_VISUAL_ONLY")!=null){views(s);return;}
   check(score(s,"$selectedMap","CmdData")==25,"Normal voting selects map 25");check(!tagged(s,"AxolotlTreehousePoster").isEmpty(),"Voting poster display exists");
   var points=tagged(s,"PlayerSpawn");check(points.size()==32&&tagged(s,"ScrapSpawn").size()==32,"32 player/scrap markers all belong to the island");
   for(var e:points){p.setPos(e.position());check(s.overworld().noCollision(p,p.getBoundingBox()),"Native clear player volume "+e.position());check(s.overworld().getBlockCollisions(p,p.getBoundingBox().move(0,-.03,0)).iterator().hasNext(),"Native solid support "+e.position());
    int ways=0;for(int[]d:new int[][]{{1,0},{-1,0},{0,1},{0,-1}}){boolean safe=false;for(int dy=-1;dy<=1;dy++){var bb=p.getBoundingBox().move(d[0],dy,d[1]);if(s.overworld().noCollision(p,bb)&&s.overworld().getBlockCollisions(p,bb.move(0,-.03,0)).iterator().hasNext())safe=true;}if(safe)ways++;}check(ways>=2,"Two native onward routes "+e.position());
   }
   check(tagged(s,"AxolotlTreehouseDecor").size()==11,"All 11 source entities are loaded");cmd(s,"function axolotl_treehouse:activate");check(tagged(s,"AxolotlTreehouseRuntime").size()==33,"Repeated activation has exactly 33 markers");
   cmd(s,"tag @a add queued");cmd(s,"tag @a add autoqueue");cmd(s,"tag @a remove spectating");cmd(s,"scoreboard players reset @a dead");cmd(s,"team join nametags @a");cmd(s,"scoreboard players set $queued CmdData 4");cmd(s,"scoreboard players set $startcountdown CmdData 2");cmd(s,"scoreboard players set $start CmdData 1");cmd(s,"function mcm:lobby/start");phase=2;ticks=0;
  }else if(phase==2&&++ticks>=400){
   check(score(s,"$gamestate","CmdData")==1,"Four-player round survives role assignment and grace");
   for(var a:s.getPlayerList().getPlayers())check(!a.isSpectator()&&Math.abs(a.getX()-57600)<60&&Math.abs(a.getZ()-57600)<60,"Participant starts on island: "+a.getScoreboardName());
   prepare(s,p);BlockPos pool=null;
   search:for(int y=74;y<=90;y++)for(int x=57583;x<57617;x++)for(int z=57582;z<57619;z++){
    var pos=new BlockPos(x,y,z);if(!s.overworld().getFluidState(pos).is(net.minecraft.tags.FluidTags.WATER))continue;p.setPos(x+.5,y+.1,z+.5);if(s.overworld().noCollision(p,p.getBoundingBox())){pool=pos;break search;}
   }
   check(pool!=null,"Found original island pond with clear player collision volume");probe(s,p,pool.getX()+.5,pool.getY()+.1,pool.getZ()+.5);check(score(s,p.getScoreboardName(),"dead")==0,"Original island water is harmless during active play");
   prepare(s,p);probe(s,p,57658.5,64.2,57600.5);check(score(s,p.getScoreboardName(),"dead")==0,"Air just above lake remains safe");
   prepare(s,p);cmd(s,"scoreboard players set $gamestate CmdData 0");p.teleportTo(57658.5,63.8,57600.5);cmd(s,"function axolotl_treehouse:waiting_tick");check(p.getY()>64&&!p.isSpectator(),"Waiting lake fall returns to safe island spawn");
   prepare(s,p);cmd(s,"scoreboard players set $graceperiod CmdData 100");probe(s,p,57658.5,63.8,57600.5);check(score(s,p.getScoreboardName(),"dead")==1&&p.isSpectator(),"Lake fall eliminates from round start, including grace");
   prepare(s,p);probe(s,p,57658.5,63.8,57600.5);check(score(s,p.getScoreboardName(),"dead")==1,"Lake fall eliminates after grace");
   prepare(s,p);probe(s,p,57750,120,57600);check(score(s,p.getScoreboardName(),"dead")==1,"Mainland mountain escape is eliminated");
   prepare(s,p);cmd(s,"scoreboard players set $graceperiod CmdData 100");probe(s,p,57750,120,57600);check(!p.isSpectator()&&p.getX()<57664,"Grace hard-boundary escape returns safely");
   prepare(s,p);p.setGameMode(GameType.SPECTATOR);probe(s,p,57658.5,63.8,57600.5);check(score(s,p.getScoreboardName(),"dead")==0,"Spectators excluded");
   prepare(s,p);cmd(s,"tag "+p.getScoreboardName()+" remove queued");probe(s,p,57658.5,63.8,57600.5);check(!p.isSpectator(),"Nonparticipants excluded");
   prepare(s,p);cmd(s,"scoreboard players set $selectedMap CmdData 22");probe(s,p,57658.5,63.8,57600.5);check(!p.isSpectator(),"Other maps excluded");
   prepare(s,p);p.teleportTo(57600.5,88,57600.5);cmd(s,"reload");phase=3;ticks=0;
  }else if(phase==3&&++ticks>=80){
   check(tagged(s,"AxolotlTreehouseRuntime").size()==33,"Active reload preserves one marker set");
   cmd(s,"scoreboard players set $gamestate CmdData 0");cmd(s,"function axolotl_treehouse:reset");check(tagged(s,"AxolotlTreehouseRuntime").isEmpty(),"Reset removes every arena marker");check(tagged(s,"AxolotlTreehouseDecor").size()==11,"Reset preserves source decorations and axolotls");
   cmd(s,"function axolotl_treehouse:activate");check(tagged(s,"AxolotlTreehouseRuntime").size()==33,"Reactivation restores exactly one marker set");
   views(s);
  }else if(phase==4){
   ++ticks;if(ticks%20==0)Minecraft.getInstance().execute(()->{var m=Minecraft.getInstance();scenicChunksReady=m.level!=null&&m.level.hasChunk(3600,3600)&&m.level.hasChunk(3588,3600)&&m.level.hasChunk(3612,3600);});
   if(ticks>=900&&scenicChunksReady){picture("treehouse-island");cmd(s,"tp BackstabbedDev 57575 82 57608 -100 5");phase=5;ticks=0;}
   if(ticks>2400)throw new AssertionError("Scenic chunks did not arrive at the client");
  }else if(phase==5&&++ticks>=60){picture("treehouse-original");cmd(s,"tp BackstabbedDev 57606 79 57604 40 0");phase=6;ticks=0;
  }else if(phase==6&&++ticks>=50){picture("treehouse-interior");cmd(s,"scoreboard players set $gamestate CmdData 0");cmd(s,"function axolotl_treehouse:reset");cmd(s,"execute positioned 28.0 2.0 89.0 as @e[type=marker,tag=MapVote,tag=AxolotlTreehouse,limit=1] run function mcm:lobby/voting/map_position_id");cmd(s,"tp BackstabbedDev 22.4 2 90 -90 0");phase=7;ticks=0;
  }else if(phase==7&&++ticks>=70){picture("treehouse-voting");phase=8;ticks=0;
  }else if(phase==8&&++ticks>=20)finish(null);
 }catch(Throwable f){f.printStackTrace();finish(f);}}
 private void finish(Throwable f){phase=-1;try{var trace=new java.io.StringWriter();if(f!=null)f.printStackTrace(new java.io.PrintWriter(trace));Files.writeString(Path.of(System.getenv("ARENA_CHECK_DIR"),"results.txt"),(f==null?"PASS\n":"FAIL "+f+"\n"+trace)+String.join("\n",results));}catch(Exception e){e.printStackTrace();}Minecraft.getInstance().execute(()->Minecraft.getInstance().stop());}
}
