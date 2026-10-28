"""Bounded KLUT-27 water-surround/entity repair. Back up saves before --apply.

Coordinates in the manifest are standalone coordinates; main-world offset is
36864 on X/Z. Only changed Anvil slots are rewritten (all other slots preserved).
"""
from pathlib import Path
from io import BytesIO
import argparse, copy, gzip, json, math, struct, time, uuid, zlib
import nbtlib as nbt
from klut27_geometry import ROOT, read_blocks, short

STAGE=ROOT/'map-previewer/maps/klut27/decor'
MANIFEST=ROOT/'docs/arenas/klut27-decor.json'
MATERIALS={'stripped_acacia_wood':'orange_terracotta','stripped_mangrove_wood':'red_terracotta',
 'stripped_birch_wood':'smooth_sandstone','stripped_dark_oak_wood':'brown_terracotta',
 'stripped_jungle_wood':'terracotta','stripped_spruce_wood':'brown_terracotta',
 'cherry_wood':'brown_terracotta','mangrove_wood':'red_terracotta'}
ENTITIES=[{'id':'iron_golem','uuid':[-1320801167,-901363419,-1545393136,-561806550],
 'position':[9.5,15,45.5],'fixed':False},
 {'id':'villager','uuid':[-887769658,-177321878,-1634696109,-940362132],
 'position':[12.5,15,33.5],'fixed':True}]

def prepare():
 b=read_blocks();water={p for p,s in b.items() if short(s)=='water' or str(s.get('Properties',{}).get('waterlogged'))=='true'}
 adjacent={tuple(p[i]+d[i] for i in range(3)) for p in water for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))}
 changes=[{'pos':list(p),'before':short(b[p]),'after':MATERIALS[short(b[p])]} for p in sorted(adjacent) if p in b and short(b[p]) in MATERIALS]
 manifest={'scope':'KLUT-27 water-adjacent flammable full cubes, main-deck golem, Pawn Shop resident','offset':[36864,0,36864],'blocks':changes,'entities':ENTITIES}
 MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
 STAGE.mkdir(parents=True,exist_ok=True)
 origin=[min(p[i] for p in b) for i in range(3)];size=[max(p[i] for p in b)-origin[i]+1 for i in range(3)]
 preview={p:copy.deepcopy(s) for p,s in b.items()}
 for c in changes:preview[tuple(c['pos'])]={'Name':'minecraft:'+c['after']}
 def state(s):
  props=s.get('Properties',{});return str(s['Name'])+('['+','.join(f'{k}={v}' for k,v in props.items())+']' if props else '')
 rows=[[[p[i]-origin[i] for i in range(3)],state(s)] for p,s in preview.items()]
 (STAGE/'preview-blocks.json').write_text(json.dumps(rows),encoding='utf-8')
 (STAGE/'repair.mjs').write_text("import fs from 'node:fs';\nexport default function(api){const s=api.createStructure("+json.dumps(size)+");for(const [p,b] of JSON.parse(fs.readFileSync(new URL('./preview-blocks.json',import.meta.url),'utf8')))api.setBlock(s,p,b);return {structure:s,metadata:{name:'klut27-decor-preview'}};}\n",encoding='utf-8')
 (STAGE/'origin.json').write_text(json.dumps(origin))
 print('Prepared',len(changes),'block replacements',json.dumps(MATERIALS))

class Region:
 def __init__(self,path):self.path=path;self.raw=bytearray(path.read_bytes());self.loaded={};self.dirty=set()
 def get(self,slot):
  if slot not in self.loaded:
   loc=struct.unpack_from('>I',self.raw,slot*4)[0]
   if not loc:return None
   off=(loc>>8)*4096;length=struct.unpack_from('>I',self.raw,off)[0];kind=self.raw[off+4];payload=bytes(self.raw[off+5:off+4+length])
   assert kind in (1,2,3),kind
   self.loaded[slot]=nbt.File.parse(BytesIO(gzip.decompress(payload) if kind==1 else zlib.decompress(payload) if kind==2 else payload))
  return self.loaded[slot]
 def encoded(self):
  raw=self.raw.copy()
  for slot in sorted(self.dirty):
   out=BytesIO();self.loaded[slot].write(out);p=zlib.compress(out.getvalue());count=(len(p)+5+4095)//4096
   assert count<256
   off=(len(raw)+4095)//4096;raw.extend(b'\0'*(off*4096-len(raw)))
   raw.extend((struct.pack('>I',len(p)+1)+b'\x02'+p).ljust(count*4096,b'\0'))
   struct.pack_into('>I',raw,slot*4,(off<<8)|count);struct.pack_into('>I',raw,4096+slot*4,int(time.time()))
  return bytes(raw)

def decode(states):
 pal=states['palette'];bits=max(4,(len(pal)-1).bit_length());per=64//bits
 if len(pal)==1:return [0]*4096
 data=[int(v)&((1<<64)-1) for v in states['data']]
 return [(data[i//per]>>((i%per)*bits))&((1<<bits)-1) for i in range(4096)]

def encode(states,values):
 bits=max(4,(len(states['palette'])-1).bit_length());per=64//bits;packed=[0]*math.ceil(4096/per)
 for i,v in enumerate(values):packed[i//per]|=v<<((i%per)*bits)
 states['data']=nbt.LongArray([v if v<1<<63 else v-(1<<64) for v in packed])

def translated_uuid(values,offset):
 if not offset:return values
 raw=uuid.uuid5(uuid.NAMESPACE_URL,'backstabbed:klut27:'+','.join(map(str,values))).bytes
 return [int.from_bytes(raw[i:i+4],'big',signed=True) for i in range(0,16,4)]

def plan(world,offset,manifest):
 regions={};sections={}
 def region(kind,cx,cz):
  p=world/kind/f'r.{cx//32}.{cz//32}.mca'
  if p not in regions:regions[p]=Region(p)
  return regions[p],(cz%32)*32+cx%32
 for change in manifest['blocks']:
  x,y,z=change['pos'];x+=offset;z+=offset;r,slot=region('region',x//16,z//16);c=r.get(slot)
  s=next(s for s in c['sections'] if int(s['Y'])==y//16)['block_states'];key=(r.path,slot,y//16)
  if key not in sections:sections[key]=(s,decode(s))
  _,values=sections[key];index=(y%16)*256+(z%16)*16+x%16
  old=short(s['palette'][values[index]])
  assert old in (change['before'],change['after']),(world,(x,y,z),old,change)
  if old==change['after']:continue
  new=nbt.Compound({'Name':nbt.String('minecraft:'+change['after'])})
  if new not in s['palette']:s['palette'].append(new)
  values[index]=s['palette'].index(new);r.dirty.add(slot)
 for (path,slot,sy),(s,values) in sections.items():
  if slot in regions[path].dirty:encode(s,values)
 # Search only the two arena entity regions, keeping unrelated entities intact.
 found={}
 for p in sorted((world/'entities').glob('*.mca')):
  rx,rz=map(int,p.stem.split('.')[1:])
  if not (offset//512-1<=rx<=offset//512 and offset//512<=rz<=offset//512):continue
  r=regions.setdefault(p,Region(p))
  for slot in range(1024):
   c=r.get(slot)
   if c is None:continue
   for e in list(c.get('Entities',[])):
    for spec in manifest['entities']:
     if list(map(int,e.get('UUID',[])))==translated_uuid(spec['uuid'],offset):
      if spec['id'] in found:
       assert found[spec['id']] is e,'Duplicate entity UUID'
       continue
      found[spec['id']]=e
      assert str(e['id'])=='minecraft:'+spec['id']
      pos=[spec['position'][0]+offset,spec['position'][1],spec['position'][2]+offset]
      e['Pos']=nbt.List[nbt.Double](pos);e['Motion']=nbt.List[nbt.Double]([0,0,0]);e['FallDistance']=nbt.Float(0);e['OnGround']=nbt.Byte(1)
      e['PersistenceRequired']=nbt.Byte(1)
      if spec['fixed']:
       e['NoAI']=nbt.Byte(1);e['Rotation']=nbt.List[nbt.Float]([-90,0])
       e.pop('SleepingX',None);e.pop('SleepingY',None);e.pop('SleepingZ',None)
      target,tslot=region('entities',math.floor(pos[0])//16,math.floor(pos[2])//16)
      tc=target.get(tslot);assert tc is not None,'Expected existing destination entity chunk'
      if target is not r or tslot!=slot:c['Entities'].remove(e);tc.setdefault('Entities',nbt.List[nbt.Compound]()).append(e);target.dirty.add(tslot)
      r.dirty.add(slot)
 assert len(found)==2,(world,found)
 return {p:r.encoded() for p,r in regions.items() if r.dirty}

def main():
 a=argparse.ArgumentParser();a.add_argument('--prepare',action='store_true');a.add_argument('--apply',action='store_true');a.add_argument('--world',type=Path);a.add_argument('--offset',type=int,default=0);args=a.parse_args()
 if args.prepare:prepare();return
 assert args.world
 outputs=plan(args.world,args.offset,json.loads(MANIFEST.read_text()))
 print('Validated',args.world,len(outputs),'affected regions')
 if args.apply:
  for p,data in outputs.items():
   temp=p.with_suffix('.mca.repair-tmp');temp.write_bytes(data);temp.replace(p)
  print('Applied')

if __name__=='__main__':main()
