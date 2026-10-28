"""Rebuild KLUT-27 spawn routes/orientations and its cuboid arena predicate.

Only edits the gameplay datapack and manifest, never terrain or entities.
Requires stopped, backed-up source and installed main saves.
"""
import json,math,re,zipfile
from collections import deque
import klut27_geometry as geom
from sync_klut27_standalone import ROOT,TARGETS,OFFSET,World,zip_bytes

def main():
 w=World(TARGETS[0],OFFSET)
 blocks={}
 for y in range(-64,47):
  for z in range(-2,51):
   for x in range(-5,25):
    s=w.get((x,y,z))
    if geom.short(s) not in ('air','cave_air','void_air'):blocks[(x,y,z)]=s
 geom.read_blocks=lambda:blocks
 _,graph,components,_=geom.analyze()
 path=ROOT/'docs/arenas/klut27.json';manifest=json.loads(path.read_text())
 chosen=[tuple(map(math.floor,p)) for p in manifest['source_player_spawns']]
 chosen[2]=(4,15,44);chosen[13]=(12,15,47)
 anchor=(9,16,15);parents={anchor:None};queue=deque([anchor])
 while queue:
  p=queue.popleft()
  for q in sorted(graph[p]):
   if q not in parents:parents[q]=p;queue.append(q)
 rotations=[];routes=[]
 for p in chosen:
  assert p in parents,p
  route=[];cur=p
  while cur is not None:route.append(list(cur));cur=parents[cur]
  routes.append(route)
  choices=[]
  for dx,dz,yaw in [(0,1,0),(-1,0,90),(0,-1,-180),(1,0,-90)]:
   run=0
   for step in range(1,6):
    q=(p[0]+dx*step,p[1],p[2]+dz*step)
    if not geom.safe(blocks,q):break
    run=step
   if run:
    q=(p[0]+dx,p[1],p[2]+dz)
    exits=len(graph.get(q,[]));choices.append((run,exits,-abs(q[0]-8)-abs(q[2]-28),yaw))
  assert choices,p
  rotations.append(max(choices)[3])
 from klut27_boundary import current_boxes
 boxes=current_boxes()
 predicate={'condition':'minecraft:any_of','terms':[{'condition':'minecraft:location_check','predicate':{'dimension':'minecraft:overworld','position':box}} for box in boxes]}
 newlines=[]
 for (x,y,z),yaw in zip(chosen,rotations):
  newlines.append(f'summon marker {x+OFFSET+.5:g} {y} {z+OFFSET+.5:g} {{Tags:["PlayerSpawn","ScrapSpawn","MapEntity","Klut27Runtime"],Rotation:[{yaw}.0f,0.0f],data:{{gravity_direction:"down",gravity_strength:1.0d}}}}')
 outputs={}
 for world in TARGETS:
  pack=world/'datapacks/mcm.zip'
  with zipfile.ZipFile(pack) as z:files={n:z.read(n) for n in z.namelist()}
  name='data/klut27/function/activate.mcfunction';lines=files[name].decode().replace('\r','').splitlines();index=0
  for i,line in enumerate(lines):
   if line.startswith('summon marker') and '"PlayerSpawn"' in line:lines[i]=newlines[index];index+=1
  assert index==28
  files[name]=('\n'.join(line for line in lines if line.strip())+'\n').encode()
  files['data/klut27/predicate/arena.json']=(json.dumps(predicate,separators=(',',':'))+'\n').encode()
  outputs[pack]=zip_bytes(files)
 for pack,data in outputs.items():
  tmp=pack.with_suffix('.zip.tmp');tmp.write_bytes(data);tmp.replace(pack)
 manifest.update(source_player_spawns=[[x+.5,y,z+.5] for x,y,z in chosen],destination_player_spawns=[[x+OFFSET+.5,y,z+OFFSET+.5] for x,y,z in chosen],spawn_rotations=[[yaw,0] for yaw in rotations],spawn_routes_source=routes,containment_boxes=boxes)
 path.write_text(json.dumps(manifest,indent=2)+'\n')
 print('Updated 28 shared player/scrap points; moved #3/#14; yaw:',rotations)
 print('Current-geometry boundary boxes:',len(boxes))

if __name__=='__main__':main()
