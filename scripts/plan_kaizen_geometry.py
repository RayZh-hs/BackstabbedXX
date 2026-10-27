#!/usr/bin/env python3
"""Recreate geometry analysis from preserved source previews and actual saved blocks.
Requires nbtlib; run from repository root after import. No world writes.
"""
from pathlib import Path
from collections import deque,Counter,defaultdict
from functools import lru_cache
import json,sys,math
import nbtlib as n
sys.path.insert(0,'scripts');sys.path.insert(0,'tests')
from test_subway_station import StationBlocks
from import_kaizen_bases import MAPS,ROOT,WORK
# Collision methods are reused with the independently audited 1.21.4 fixture.
SHAPES=json.loads((ROOT/'tests/fixtures/kaizen_collision_shapes.json').read_text())['states']
class Blocks(StationBlocks):
 @lru_cache(None)
 def shapes(self,x,y,z):
  st=self.state(x,y,z);key=st['Name']+'['+','.join(f'{k}={v}'for k,v in sorted(st.get('Properties',{}).items()))+']';return SHAPES[key]
 def hazard(self,x,y,z):
  st=self.state(x,y,z);s=st['Name'].split(':')[1]
  return (s in {'water','lava','fire','soul_fire','magma_block','cactus','sweet_berry_bush','powder_snow','wither_rose','bubble_column'} or st.get('Properties',{}).get('waterlogged')=='true' or (s in ('campfire','soul_campfire') and st.get('Properties',{}).get('lit')=='true'))
b=Blocks()
for spec in MAPS:
 ns=spec['namespace'];p=ROOT/'map-previewer/maps'/spec['slug'];meta=json.loads((p/'preview.json').read_text());st=n.load((WORK/'repairs'/(ns+'-context.nbt')) if ns!='bagger_288' else p/'preview.nbt');origin=meta['origin'];d=spec['translation']
 excluded={'air','water','cave_air','void_air','light','barrier','structure_void'}
 if ns=='underwater_base':excluded|={'sand','sandstone','gravel','stone','dirt','clay','granite','diorite','andesite','seagrass','tall_seagrass','kelp','kelp_plant','sea_pickle','magma_block','mud','suspicious_sand'}
 artifact=set()
 for block in st['blocks']:
  name=str(st['palette'][int(block['state'])]['Name']).split(':')[1]
  if name in excluded or (ns=='underwater_base' and ('coral' in name or name.endswith('_ore'))):continue
  pt=tuple(int(block['pos'][a])+origin[a]+d[a]for a in range(3))
  artifact.add(pt)
 # Keep the largest physically connected set, excluding detached buoys/solar rafts.
 left=set(artifact);components=[]
 while left:
  seed=left.pop();pending=[seed];seen={seed}
  while pending:
   x,y,z=pending.pop()
   for dx,dy,dz in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
    q=x+dx,y+dy,z+dz
    if q in left:left.remove(q);seen.add(q);pending.append(q)
  components.append(seen)
 components.sort(key=len,reverse=True);main=components[0]
 print(ns,'component sizes',[len(c)for c in components[:12]],flush=True)
 # Safe feet candidates on full-width cube or slab surfaces of the main object.
 candidates={}
 for x,y,z in main:
  shapes=b.shapes(x,y,z)
  surfaces={s[4]for s in shapes if s[0]<=.2 and s[2]<=.2 and s[3]>=.8 and s[5]>=.8}
  for h in surfaces:
   feet=y+h
   if b.clear(x+.5,feet,z+.5) and not any(b.hazard(x,yy,z)for yy in range(y,math.floor(feet+1.8)+1)):
    candidates[(x,round(feet,4),z)]=(x+.5,round(feet,4),z+.5)
 # Step graph allows jumps up one block, and drops one block; clear midpoint.
 def neighbors(p):
  x,y,z=p
  for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)]:
   for yy in heights.get((x+dx,z+dz),[]):
    if abs(yy-y)>1.001:continue
    top=max(y,yy)
    if b.clear(x+.5,top,z+.5) and b.clear(x+dx+.5,top,z+dz+.5) and b.clear(x+dx*.5+.5,top,z+dz*.5+.5):yield (x+dx,yy,z+dz)
 heights=defaultdict(list)
 for x,y,z in candidates:heights[x,z].append(y)
 left=set(candidates);walk_components=[]
 while left:
  seed=left.pop();seen={seed};pending=[seed]
  while pending:
   p0=pending.pop()
   for q in neighbors(p0):
    if q in left:left.remove(q);seen.add(q);pending.append(q)
  walk_components.append(seen)
 walk_components.sort(key=len,reverse=True)
 print(ns,'walk components',[(len(c),Counter(p[1]for p in c).most_common(6))for c in walk_components[:12]],flush=True)
 # Record conservative graph for spawn planning; source coords retained.
 output={'namespace':ns,'artifact_blocks':len(main),'artifact':sorted(main),'walk_components':[[list(p)for p in sorted(c)]for c in walk_components[:12]],'candidate_count':len(candidates)}
 (WORK/(ns+'-geometry.json')).write_text(json.dumps(output))
