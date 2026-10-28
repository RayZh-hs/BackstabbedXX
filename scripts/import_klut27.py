"""Import KLUT-27 without geometry changes into unused regions (offset 36864).

Requires verified full-save backups and a stopped destination world. Leaves the
original download/source, destination level.dat and gameplay ZIP untouched.
"""
from collections import Counter
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import uuid
import nbtlib as nbt
from import_subway_station import write_regions
from klut27_elevators import ROOT, SOURCE
from klut27_geometry import OFFSET

WORLD = ROOT / '.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies'
SOURCE_URL='https://www.planetminecraft.com/project/klut-27-spaceship-mothership-space-station-work-in-progress/'

def translate_entity(e):
    e=copy.deepcopy(e)
    for key in ('Pos',):
        if key in e:
            e[key][0]=nbt.Double(float(e[key][0])+OFFSET)
            e[key][2]=nbt.Double(float(e[key][2])+OFFSET)
    for key in ('TileX','SleepingX','BoundX'):
        if key in e: e[key]=nbt.Int(int(e[key])+OFFSET)
    for key in ('TileZ','SleepingZ','BoundZ'):
        if key in e: e[key]=nbt.Int(int(e[key])+OFFSET)
    for memory in e.get('Brain',{}).get('memories',{}).values():
        value=memory.get('value',{})
        if isinstance(value,dict) or isinstance(value,nbt.Compound):
            if 'pos' in value:
                value['pos'][0]+=OFFSET;value['pos'][2]+=OFFSET
    if 'Leash' in e and 'X' in e['Leash']:
        e['Leash']['X']+=OFFSET;e['Leash']['Z']+=OFFSET
    if 'Passengers' in e:
        e['Passengers']=nbt.List[nbt.Compound]([translate_entity(p) for p in e['Passengers']])
    old=','.join(str(int(v)) for v in e.get('UUID',[]))
    raw=uuid.uuid5(uuid.NAMESPACE_URL,'backstabbed:klut27:'+old).bytes
    e['UUID']=nbt.IntArray([int.from_bytes(raw[i:i+4],'big',signed=True) for i in range(0,16,4)])
    e.setdefault('Tags',nbt.List[nbt.String]()).append(nbt.String('Klut27Decoration'))
    return e

def main():
    spec=importlib.util.spec_from_file_location('exporter',ROOT/'map-previewer/export-java-world.py')
    exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)
    chunks=[];entities=[];tiles=Counter();types=Counter();disabled=[]
    for original in exporter.chunks(SOURCE/'region'):
        sx,sz=int(original['xPos']),int(original['zPos'])
        if not (-1<=sx<=1 and -1<=sz<=3):continue
        chunk=copy.deepcopy(original);cx,cz=sx+OFFSET//16,sz+OFFSET//16
        chunk['xPos'],chunk['zPos']=nbt.Int(cx),nbt.Int(cz)
        for tile in chunk.get('block_entities',[]):
            tiles[str(tile['id'])]+=1
            if str(tile['id'])=='minecraft:command_block':
                disabled.append({'source':[int(tile[k]) for k in ('x','y','z')],'command':str(tile.get('Command',''))})
                tile['Command']=nbt.String('');tile['auto']=nbt.Byte(0);tile['powered']=nbt.Byte(0)
                tile.pop('LastOutput',None)
            tile['x']=nbt.Int(int(tile['x'])+OFFSET);tile['z']=nbt.Int(int(tile['z'])+OFFSET)
        for key in ('block_ticks','fluid_ticks'):
            for tick in chunk.get(key,[]):
                tick['x']=nbt.Int(int(tick['x'])+OFFSET);tick['z']=nbt.Int(int(tick['z'])+OFFSET)
        assert not any(chunk.get('structures',{}).get(k) for k in ('starts','References'))
        chunks.append((cx,cz,chunk))
    assert len(chunks)==15
    for original in exporter.chunks(SOURCE/'entities'):
        sx,sz=map(int,original['Position'])
        if not (-1<=sx<=1 and -1<=sz<=3):continue
        translated=[]
        for entity in original.get('Entities',[]):
            types[str(entity['id'])]+=1
            translated.append(translate_entity(entity))
        chunk=copy.deepcopy(original)
        chunk['Position']=nbt.IntArray([sx+OFFSET//16,sz+OFFSET//16])
        chunk['Entities']=nbt.List[nbt.Compound](translated)
        entities.append((sx+OFFSET//16,sz+OFFSET//16,chunk))
    outputs=write_regions(WORLD/'region',chunks)
    outputs.update(write_regions(WORLD/'entities',entities))
    assert all(not p.exists() for p in outputs)
    for path,data in outputs.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    report={'title':'KLUT-27','creator':'Bekulainen','source_url':SOURCE_URL,'namespace':'klut27','map_id':20,
        'reuse_terms':'Author requires permission before reuse in own builds, attribution and original page link. Local requested integration only; permission not established for publication.',
        'source_archive_sha256':hashlib.sha256((SOURCE.parent/'klut-27.zip').read_bytes()).hexdigest(),
        'source_version':'1.20.4','source_data_version':3700,'target_version':'1.21.4',
        'transform':{'translation':[OFFSET,0,OFFSET],'rotation_degrees':0},
        'source_visible_bounds':{'min':[-5,-64,-2],'max':[24,46,50]},
        'destination_visible_bounds':{'min':[OFFSET-5,-64,OFFSET-2],'max':[OFFSET+24,46,OFFSET+50]},
        'imported_chunk_bounds':{'min':[OFFSET-16,-64,OFFSET-16],'max':[OFFSET+31,319,OFFSET+63]},
        'imported_chunks':len(chunks),'block_entities':dict(tiles),'decorative_entities':dict(types),
        'disabled_source_commands':disabled,
        'regions':{str(p.relative_to(ROOT)):hashlib.sha256(v).hexdigest() for p,v in outputs.items()}}
    (ROOT/'docs/arenas/klut27.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
