#!/usr/bin/env python3
"""Select distributed spawns and derive containment masks from saved geometry.
Run after plan_kaizen_geometry.py; updates integration reports, never blocks.
Requires nbtlib and preserved source preview artifacts.
"""
import sys,json,math
from pathlib import Path
from collections import defaultdict
sys.path.insert(0,'scripts');sys.path.insert(0,'tests')
from import_kaizen_bases import MAPS,ROOT,WORK
from test_subway_station import StationBlocks
from functools import lru_cache
SHAPES=json.loads((ROOT/'tests/fixtures/kaizen_collision_shapes.json').read_text())['states']
class Blocks(StationBlocks):
 @lru_cache(None)
 def shapes(self,x,y,z):
  st=self.state(x,y,z);key=st['Name']+'['+','.join(f'{k}={v}' for k,v in sorted(st.get('Properties',{}).items()))+']';return SHAPES[key]
b=Blocks()
def rectangles(mask):
 rows=defaultdict(list)
 for x,z in mask:rows[z].append(x)
 active={};out=[]
 for z in range(min(rows),max(rows)+2):
  xs=sorted(set(rows[z]));runs=[]
  for x in xs:
   if runs and x==runs[-1][1]+1:runs[-1][1]=x
   else:runs.append([x,x])
  keys=set(map(tuple,runs))
  for key in set(active)-keys:
   z0,z1=active.pop(key);out.append([key[0],key[1]+1,z0,z1+1])
  for key in keys:
   active[key]=[active[key][0],z] if key in active else [z,z]
 return out
for sp in MAPS:
 ns=sp['namespace'];d=sp['translation'];g=json.loads((WORK/(ns+'-geometry.json')).read_text());comps=g['walk_components']
 if ns=='meridian_base':groups=[(comps[1],12,lambda p:-29.01<=p[1]<=-28.9),(comps[0],12,lambda p:-20.01<=p[1]<=-19.9)];bands=[(-32,-23),(-23,-16),(-16,-8),(-8,0),(0,22)]
 elif ns=='bagger_288':groups=[(comps[2]+comps[5],8,lambda p:p[1]==-40),(comps[3],8,lambda p:-35.01<=p[1]<=-34.9),(comps[0],8,lambda p:p[1]==-27)];bands=[(-50,-41),(-41,-30),(-30,-20),(-20,-10),(-10,0),(0,13),(13,47)]
 else:groups=[(comps[3],8,lambda p:p[1]==43),(comps[0],8,lambda p:p[1]==43),(comps[1],8,lambda p:p[1]==43)];bands=[(40,47),(47,54),(54,66)]
 spawns=[];paths=[]
 for pool,count,accept in groups:
  s=set(map(tuple,pool));candidates=[]
  for x,y,z in sorted(s):
   if not accept((x,y,z)):continue
   # At least two clear supported steps out; each endpoint is an actual saved surface.
   exits=[]
   for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)]:
    q=(x+dx,y,z+dz)
    if q in s and b.clear(x+dx*.5+.5,y,z+dz*.5+.5):exits.append(q)
   if len(exits)>=2:candidates.append(((x+.5,y,z+.5),exits))
  print(ns,'pool',len(candidates),'need',count,flush=True)
  chosen=[]
  for i in range(count):
   if not chosen:
    mean=[sum(p[0][a]for p in candidates)/len(candidates)for a in range(3)];candidate=min(candidates,key=lambda p:sum((p[0][a]-mean[a])**2 for a in range(3)))
   else:candidate=max(candidates,key=lambda p:min(sum((p[0][a]-v[a])**2 for a in range(3))for v in chosen))
   point,exits=candidate
   if chosen:assert min(sum((point[a]-v[a])**2 for a in range(3))for v in chosen)>=4,(ns,point)
   chosen.append(point);candidates.remove(candidate);paths.append({'spawn':point,'exits':[[x+.5,y,z+.5]for x,y,z in exits]})
  spawns+=chosen
 # Containment follows the connected architecture at each height, excluding
 # detached scenery and low source terrain. No physical barriers are installed.
 terms=[];boxes=[]
 for lo,hi in bands:
  projected={(x,z)for x,y,z in g['artifact']if lo-2<=y<=hi}
  if not projected:continue
  mask={(x+dx,z+dz)for x,z in projected for dx in (-1,0,1)for dz in (-1,0,1)}
  for x0,x1,z0,z1 in rectangles(mask):
   box={'x':{'min':x0,'max':x1},'y':{'min':lo,'max':hi},'z':{'min':z0,'max':z1}};boxes.append(box)
   terms.append({'condition':'minecraft:location_check','predicate':{'dimension':'minecraft:overworld','position':box}})
 predicate={'condition':'minecraft:any_of','terms':terms}
 def inside(p):return any(all(box[a]['min']<=v<=box[a]['max']for a,v in zip('xyz',p))for box in boxes)
 assert all(inside(p)for p in spawns)
 report=json.loads((ROOT/('docs/arenas/'+ns+'.json')).read_text());report.update({'destination_player_spawns':spawns,'source_player_spawns':[[p[a]-d[a]for a in range(3)]for p in spawns],'spawn_exit_checks':paths,'return_position':spawns[0],'spectator_position':[spawns[0][0],spawns[0][1]+3,spawns[0][2]],'boundary_boxes':boxes,'connected_artifact_blocks':g['artifact_blocks'],'spawn_selection':('Ring deck and upper main-platform walking surfaces' if ns=='meridian_base' else 'Three main-body working decks' if ns=='bagger_288' else 'Dry interiors of the three connected main modules'),'containment':('Per-height masks of the connected build, one-block movement margin; out-of-mask, fluid or wrong-dimension live participants are eliminated via mcm:game/playerdeath during active rounds, including grace. Waiting participants return to a validated spawn. Spectators, dead/lobby players, inactive states and other arenas excluded.' if ns=='meridian_base' else 'Per-height masks of the connected build, one-block movement margin; out-of-mask, fluid or wrong-dimension live participants return to a validated spawn. Spectators, dead/lobby players, inactive states and other arenas excluded.')})
 lower=[min(p[a] for p in g['artifact']) for a in range(3)];upper=[max(p[a] for p in g['artifact']) for a in range(3)]
 report['main_connected_destination_bounds']={'min':lower,'max':upper}
 report['main_connected_source_bounds']={'min':[lower[a]-d[a] for a in range(3)],'max':[upper[a]-d[a] for a in range(3)]}
 (ROOT/('docs/arenas/'+ns+'.json')).write_text(json.dumps(report,indent=2)+'\n');(WORK/(ns+'-predicate.json')).write_text(json.dumps(predicate,indent=2)+'\n');print(ns,'spawns',len(spawns),'region boxes',len(boxes),flush=True)
