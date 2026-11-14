"""Prepare the native Minecraft terrain sample for a scenic lake basin."""
from pathlib import Path
from io import BytesIO
import sys,json,math,collections,gzip
import nbtlib as n
import numpy as np
from scipy.ndimage import label, binary_fill_holes, distance_transform_edt
import native_trees
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'arena-editor'))
from world import read_region
base=ROOT/'map-previewer/maps/axolotl-treehouse';selection=json.loads((ROOT/'dev/axolotl-treehouse/terrain-sample/selection.json').read_text());center=selection['center'];origin=[center[0]-256,48,center[1]-256]
size=512;grid=np.zeros((272,size,size),dtype=np.uint16);palette=[{'Name':'minecraft:air'}];ids={json.dumps(palette[0],sort_keys=True):0};count=0
for file in(base/'vanilla-sample/raw-world/region').glob('*.mca'):
 for _,raw in read_region(file).values():
  c=n.File.parse(BytesIO(raw));cx,cz=int(c['xPos']),int(c['zPos']);x0,z0=cx*16-origin[0],cz*16-origin[2]
  if not(0<=x0<size and 0<=z0<size):continue
  count+=1
  for s in c['sections']:
   sy=int(s['Y'])*16;bs=s.get('block_states')
   if sy<48 or not bs:continue
   pal=bs['palette'];lookup=[]
   for p in pal:
    p=p.unpack();key=json.dumps(p,sort_keys=True)
    if key not in ids:ids[key]=len(palette);palette.append(p)
    lookup.append(ids[key])
   if len(pal)==1:values=np.zeros(4096,dtype=np.uint16)
   else:
    bits=max(4,(len(pal)-1).bit_length());per=64//bits;index=np.arange(4096,dtype=np.uint64);packed=np.asarray(bs['data'],dtype=np.int64).view(np.uint64);values=((packed[(index//per).astype(int)]>>((index%per)*bits))&((1<<bits)-1)).astype(np.uint16)
   grid[sy-48:sy-32,z0:z0+16,x0:x0+16]=np.asarray(lookup,dtype=np.uint16)[values].reshape(16,16,16)
assert count==1024,count
soil={'grass_block','dirt','stone','andesite','diorite','granite','coarse_dirt','podzol','sand','gravel','clay','calcite','snow_block','packed_ice','tuff','rooted_dirt','moss_block'}
solid=np.asarray([p['Name'].split(':')[1]in soil for p in palette]);h=319-np.argmax(solid[grid[::-1]],axis=0)
h[~np.any(solid[grid],axis=0)]=48
trees=native_trees.extract(grid,palette)
# Close the sample's low southern valley mouth with another native ridge from
# the same world. Its interior is copied directly; a 20-block edge transition
# shifts the donor columns vertically to meet the neighbouring native ground.
ridge_patch={'source_xz':[272,48],'destination_xz':[160,384],'size_xz':[160,128],'edge_transition':20}
ridge_changed=np.zeros((512,512),dtype=bool)
for z in range(384,512):
 for x in range(160,320):
  sx,sz=x+112,z-336
  old,donor=int(h[z,x]),int(h[sz,sx])
  t=min(1,min(x-160,319-x,z-384,511-z)/20);t=t*t*(3-2*t)
  if donor<=old or t<=0:continue
  top=round(old+(donor-old)*t);shift=donor-top;column=grid[:,sz,sx].copy()
  if shift:column[:-shift]=column[shift:];column[-shift:]=0
  grid[:,z,x]=column;h[z,x]=top;ridge_changed[z,x]=True
np.savez_compressed(base/'vanilla-sample/native-height.npz',height=h)
zz,xx=np.indices(h.shape);radius=np.hypot(xx-256,zz-256)
# Follow the connected low valley, widening its water and retaining its coves.
# The central disk guarantees a broad lake around every side of the island.
labels,_=label((h<78)&(radius<145))
valley=binary_fill_holes(labels==labels[256,256])
lake=(distance_transform_edt(~valley)<36)|(radius<128)
bank_distance=distance_transform_edt(~lake)
for name in ['water','stone','dirt','grass_block']:
 p={'Name':'minecraft:'+name}
 if name=='water':p['Properties']={'level':'0'}
 if name=='grass_block':p['Properties']={'snowy':'false'}
 k=json.dumps(p,sort_keys=True)
 if k not in ids:ids[k]=len(palette);palette.append(p)
 def lookup(name):return next(i for i,p in enumerate(palette)if p['Name']=='minecraft:'+name)
# The distant landscape retains the native block columns. Only the inner basin
# is cleared/graded to provide the user's large, unobstructed lake.
for z in range(size):
 for x in range(size):
  d=float(bank_distance[z,x])
  if lake[z,x]:
   grid[:,z,x]=0;grid[7:10,z,x]=lookup('stone');grid[10:16,z,x]=lookup('water')
  elif d<34:
   top=int(h[z,x]);t=d/34;shift=max(0,round((top-63)*(1-t)))
   if shift:
    grid[:-shift,z,x]=grid[shift:,z,x];grid[-shift:,z,x]=0
   # All graded banks meet a six-block-deep lake without underwater holes.
   grid[7:10,z,x]=lookup('stone')
   for y in range(58,64):
    if grid[y-48,z,x]==0:grid[y-48,z,x]=lookup('water')
solid=np.asarray([p['Name'].split(':')[1]in soil for p in palette])
final_h=319-np.argmax(solid[grid[::-1]],axis=0)
final_h[~np.any(solid[grid],axis=0)]=48
placed_trees=native_trees.restore(grid,trees,final_h,ridge_changed)
# Store several complete native trees whose original blocks survived placement.
# A rigid translation contract catches canopy stretching in the saved arena.
tree_reference=[]
for tree in placed_trees:
 if len(tree_reference)>=6:break
 if tree['translation'][1]==0:continue
 points,states=tree['positions'],tree['states']
 if len(points)<60 or not np.all(grid[tuple(points.T)]==states):continue
 tree_reference.append({'root':[57344+tree['root'][0],tree['root'][1],57344+tree['root'][2]],'translation':tree['translation'],'blocks':[[57344+int(x),48+int(y),57344+int(z),palette[int(state)]]for (y,z,x),state in zip(points,states)]})
assert len(tree_reference)==6,len(tree_reference)
(ROOT/'axolotl-treehouse/build/vanilla-tree-reference.json.gz').write_bytes(gzip.compress(json.dumps(tree_reference,separators=(',',':')).encode(),mtime=0))
np.savez_compressed(base/'vanilla-sample/scene.npz',grid=grid,palette=json.dumps(palette))
reference=[]
for z in range(0,512,16):
 for x in range(0,512,16):
  if bank_distance[z,x]<34:continue
  y=int(h[z,x])
  if y<49:continue
  for yy in [y-1,y,y+1]:reference.append([57600+x-256,yy,57600+z-256,palette[int(grid[yy-48,z,x])]])
(ROOT/'axolotl-treehouse/build/vanilla-surface-reference.json.gz').write_bytes(gzip.compress(json.dumps(reference,separators=(',',':')).encode(),mtime=0))

report={**selection,'source':'Minecraft Java 1.21.4 normal overworld, generated natively by VanillaTerrainSample.java','source_origin':origin,'scene_size':[512,272,512],'shoreline':'native connected valley below Y78, widened 36 blocks and united with a 128-block central lake','native_columns_preserved_outside_shore_grading':True,'minimum_lake_radius':128,'shore_grading_width':34,'chunk_count':count,'seed_locator':'https://www.reddit.com/r/minecraftseeds/comments/1u47la5/im_looking_for_a_seed_similar_to_this_one_its_a/','height_range':[int(h.min()),int(h.max())]}
report['native_ridge_patch']=ridge_patch
report['native_trees']={'placement':'Each complete native log/leaf group is translated rigidly onto the finished terrain; flooded trees are omitted.','placed_tree_groups':len(placed_trees),'rigid_translation_validation_samples':len(tree_reference)}
(base/'vanilla-sample/provenance.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
# An analytical height plot helps inspect the sample; this is not map artwork.
try:
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 plt.figure(figsize=(8,8));plt.imshow(h,origin='lower',cmap='terrain',vmin=55,vmax=190);plt.colorbar();plt.contour(bank_distance,[.5,34],colors=['cyan','white']);plt.savefig(base/'vanilla-sample/native-height.png');plt.close()
except ImportError:pass
