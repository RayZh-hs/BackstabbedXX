"""Synchronize only KLUT-27 block edits; preserve destination entities and saves."""
from pathlib import Path
import copy,json,sys,zipfile,re
from io import BytesIO
import nbtlib as nbt
from repair_klut27_decor import Region,decode,encode,ROOT
LIVE=Path('C:/Users/dyf08/AppData/Roaming/PrismLauncher/instances/Backstabbed++/.minecraft/saves')
SOURCE=LIVE/'KLUT-27 - 1.21.4 Fixed'
TARGETS=[ROOT/'.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies',LIVE/'Backstabbed ++! v1.1.1 Latest 2026-10-28 77e59f6']
OFFSET=36864
STAGE=ROOT/'map-previewer/maps/klut27/sync'

class World:
 def __init__(self,path,offset=0):self.path=path;self.offset=offset;self.regions={};self.cache={}
 def chunk(self,x,z):
  x+=self.offset;z+=self.offset;cx,cz=x//16,z//16;p=self.path/'region'/f'r.{cx//32}.{cz//32}.mca'
  if p not in self.regions:self.regions[p]=Region(p)
  r=self.regions[p];slot=(cz%32)*32+cx%32
  return r,slot,r.get(slot)
 def section(self,p):
  x,y,z=p;r,slot,c=self.chunk(x,z);key=(r.path,slot,y//16)
  if key not in self.cache:
   sec=next(s for s in c['sections'] if int(s['Y'])==y//16)
   states=sec['block_states'];self.cache[key]=(states,decode(states))
  return r,slot,self.cache[key]
 def get(self,p):
  r,slot,(s,d)=self.section(p);x,y,z=p
  return s['palette'][d[(y%16)*256+(z%16)*16+x%16]]
 def set(self,p,state):
  r,slot,(s,d)=self.section(p);x,y,z=p
  if state not in s['palette']:s['palette'].append(copy.deepcopy(state))
  d[(y%16)*256+(z%16)*16+x%16]=s['palette'].index(state);r.dirty.add(slot)
 def outputs(self):
  for (p,slot,sy),(s,d) in self.cache.items():
   if slot in self.regions[p].dirty:encode(s,d)
  return {p:r.encoded() for p,r in self.regions.items() if r.dirty}

def state_json(s):return {'Name':str(s['Name']),**({'Properties':{str(k):str(v) for k,v in s['Properties'].items()}} if 'Properties' in s else {})}
def scan():
 source=World(SOURCE);target=World(TARGETS[0],OFFSET);changes=[]
 for y in range(-64,47):
  for z in range(-2,51):
   for x in range(-5,25):
    p=(x,y,z);s=source.get(p);t=target.get(p)
    if s!=t:changes.append({'pos':list(p),'before':state_json(t),'after':state_json(s)})
 STAGE.mkdir(parents=True,exist_ok=True);(STAGE/'differences.json').write_text(json.dumps(changes,indent=2)+'\n')
 from collections import Counter
 print('Block differences',len(changes));print(Counter((c['before']['Name'],c['after']['Name']) for c in changes))
 for c in changes:
  if c['before']['Name']==c['after']['Name']:print('State-only',c)
 return changes

def nbt_state(s):
 return nbt.Compound({'Name':nbt.String(s['Name']),**({'Properties':nbt.Compound({k:nbt.String(v) for k,v in s['Properties'].items()})} if s.get('Properties') else {})})

def block_string(s):
 return s['Name']+('['+','.join(f'{k}={v}' for k,v in s.get('Properties',{}).items())+']' if s.get('Properties') else '')

def vending_files(offset):
 p=[4+offset+.5,15.5,35+offset+.5]
 advancement={'criteria':{'button':{'trigger':'minecraft:default_block_use','conditions':{'location':[{'condition':'minecraft:location_check','predicate':{'dimension':'minecraft:overworld','position':{a:{'min':v,'max':v} for a,v in zip(('x','y','z'),p)},'block':{'blocks':'minecraft:oak_button'}}}]}}},'rewards':{'function':'klut27_vending:ice_cream'}}
 function='advancement revoke @s only klut27_vending:ice_cream\ntellraw @s '+json.dumps({'text':'SH*T！怎么坏了？'},ensure_ascii=False)+'\n'
 return {'data/klut27_vending/advancement/ice_cream.json':(json.dumps(advancement,indent=2)+'\n').encode(),
 'data/klut27_vending/function/ice_cream.mcfunction':function.encode('utf-8')}

def zip_bytes(files):
 out=BytesIO()
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  for name,data in files.items():z.writestr(name,data)
 return out.getvalue()

def prepare_preview():
 source=World(SOURCE);rows=[]
 for y in range(-64,47):
  for z in range(-2,51):
   for x in range(-5,25):
    state=state_json(source.get((x,y,z)))
    if state['Name'] not in ('minecraft:air','minecraft:cave_air','minecraft:void_air'):rows.append([[x+5,y+64,z+2],block_string(state)])
 (STAGE/'blocks.json').write_text(json.dumps(rows))
 (STAGE/'sync.mjs').write_text("import fs from 'node:fs';export default function(api){const s=api.createStructure([30,111,53]);for(const [p,b] of JSON.parse(fs.readFileSync(new URL('./blocks.json',import.meta.url),'utf8')))api.setBlock(s,p,b);return {structure:s,metadata:{name:'klut27-standalone-sync'}};}")

def apply():
 changes=json.loads((STAGE/'differences.json').read_text());outputs={};counts=[]
 for path,offset in [(SOURCE,0)]+[(w,OFFSET) for w in TARGETS]:
  w=World(path,offset)
  if offset:
   for c in changes:w.set(tuple(c['pos']),nbt_state(c['after']))
  r,slot,chunk=w.chunk(4,34)
  command=next(t for t in chunk['block_entities'] if tuple(int(t[k]) for k in ('x','y','z'))==(4+offset,15,34+offset))
  command['Command']=nbt.String('');command['auto']=nbt.Byte(0);command['powered']=nbt.Byte(0);command['SuccessCount']=nbt.Int(0);command.pop('LastOutput',None);r.dirty.add(slot)
  outputs.update(w.outputs())
  if offset:
   pack=path/'datapacks/mcm.zip'
   with zipfile.ZipFile(pack) as z:files={n:z.read(n) for n in z.namelist()}
   name='data/klut27/function/restore_blocks.mcfunction';lines=files[name].decode().replace('\r','').splitlines()
   for c in changes:
    x,y,z=c['pos'];prefix=f'setblock {x+offset} {y} {z+offset} '
    found=[i for i,line in enumerate(lines) if line.startswith(prefix)]
    replacement=prefix+block_string(c['after'])
    if found:lines[found[0]]=replacement
    elif c['after']['Name'].endswith(('_door','_trapdoor','_button','_pressure_plate')):lines.append(replacement)
   files[name]=('\n'.join(lines)+'\n').encode();counts.append(len(lines));files.update(vending_files(offset));outputs[pack]=zip_bytes(files)
  else:
   files={'pack.mcmeta':json.dumps({'pack':{'pack_format':61,'description':'KLUT-27 ice cream vending machine'}}).encode()};files.update(vending_files(0))
   outputs[path/'datapacks/klut27-vending.zip']=zip_bytes(files)
 # Every save and pack is prepared before any write.
 for p,data in outputs.items():
  temp=p.with_name(p.name+'.sync-tmp');temp.write_bytes(data);temp.replace(p)
 report={'block_changes':changes,'button_source':[4,15,35],'message':'SH*T！怎么坏了？','reset_commands':counts[0],
 'updated_files':[str(p) for p in outputs],'entities_unchanged':True}
 (ROOT/'docs/arenas/klut27-sync.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print('Applied',len(changes),'block states, updated files:',len(outputs),'reset count',counts)

if __name__=='__main__':
 if '--apply' in sys.argv:apply()
 else:scan();prepare_preview()
