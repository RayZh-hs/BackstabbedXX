"""Convert the original litematic for inspection without changing its blocks or states."""
import copy, hashlib, json, math
from pathlib import Path
from litemapy import Schematic
import nbtlib as n
base=Path('map-previewer/maps/axolotl-treehouse')
src=base/'source.litematic'
s=Schematic.load(str(src))
regions=list(s.regions.items())
origin=[min(getattr(r,'min_schem_'+a)() for _,r in regions) for a in 'xyz']
maximum=[max(getattr(r,'max_schem_'+a)() for _,r in regions) for a in 'xyz']
size=[maximum[i]-origin[i]+1 for i in range(3)]
blocks={};palette=[];ids={};entities=[];reports=[]
for name,r in regions:
 off=[r.x-origin[0],r.y-origin[1],r.z-origin[2]]
 tiles={tuple(map(int,t.position)):t for t in r.tile_entities}
 count=0
 for p in r.allblockpos():
  state=r[p]
  if state.id in {'minecraft:air','minecraft:cave_air','minecraft:void_air'}:continue
  value=state.to_nbt();key=value.snbt()
  if key not in ids:ids[key]=len(palette);palette.append(value)
  q=tuple(int(p[i])+off[i] for i in range(3))
  entry=n.Compound({'pos':n.List[n.Int](q),'state':n.Int(ids[key])})
  if p in tiles:
   tile=copy.deepcopy(tiles[p].data)
   for a in 'xyz':tile.pop(a,None)
   entry['nbt']=tile
  if q in blocks and int(blocks[q]['state'])!=int(entry['state']):raise ValueError('Conflicting overlapping source regions at '+str(q))
  blocks[q]=entry;count+=1
 for e in r.entities:
  pos=[float(e.position[i])+off[i]for i in range(3)]
  entities.append(n.Compound({'pos':n.List[n.Double](pos),'blockPos':n.List[n.Int]([math.floor(v)for v in pos]),'nbt':copy.deepcopy(e.data)}))
 reports.append({'name':name,'position':[r.x,r.y,r.z],'size':[r.width,r.height,r.length],'blocks':count,'block_entities':len(tiles),'entities':len(r.entities)})
out=n.File({'DataVersion':n.Int(s.mc_version),'size':n.List[n.Int](size),'palette':n.List[n.Compound](palette),'blocks':n.List[n.Compound](blocks.values()),'entities':n.List[n.Compound](entities)},gzipped=True)
out.save(base/'original-treehouse.nbt')
report={'name':'Original Water Curtain Treehouse','creator':'siyuan_日记','source_url':'https://www.bilibili.com/video/BV1fDNJ6qEpx','download_url':'https://pan.baidu.com/s/19aUMmSI5S1PpEcLJgvz_Nw?pwd=v8ch','litematic_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'litematic_name':s.name,'litematic_author':s.author,'litematic_description':s.description,'data_version':s.mc_version,'origin':origin,'size':size,'regions':reports,'palette_count':len(palette),'blocks':len(blocks),'entities':len(entities)}
(base/'original-treehouse.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
print('Palette:',[str(x['Name'])for x in palette])
