"""Pure fire connectivity rules shared by generator and regression tests."""
from collections import deque
WOOD=('oak','spruce','birch','jungle','acacia','dark_oak','mangrove','cherry','pale_oak','bamboo')
DIRS=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))

def touches(a,b):
 return a!=b and max(abs(a[i]-b[i]) for i in range(3))==1

def flammable(s):
 name=str(s['Name']).split(':')[-1]
 if str(s.get('Properties',{}).get('waterlogged','false'))=='true':return False
 if name.startswith(('crimson_','warped_','stripped_crimson_','stripped_warped_')):return False
 return (any(name.startswith(w+'_') or name.startswith('stripped_'+w+'_') for w in WOOD)
         or name.endswith(('_wool','_carpet','_banner','_wall_banner'))
         or name in {'bookshelf','chiseled_bookshelf','lectern','hay_block','scaffolding','dried_kelp_block'})

def fire_distances(blocks,seeds):
 result={p:0 for p in seeds if p in blocks and flammable(blocks[p])};q=deque(result)
 while q:
  p=q.popleft()
  for d in DIRS:
   n=tuple(p[i]+d[i] for i in range(3))
   if n not in result and n in blocks and flammable(blocks[n]):result[n]=result[p]+1;q.append(n)
 return result

