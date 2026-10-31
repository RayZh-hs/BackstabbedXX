"""Stage/install Yacht-style boundary timing in three arenas, preserving geometry."""
from pathlib import Path
from contextlib import ExitStack
import argparse,datetime,hashlib,json,sys,zipfile
from klut27_mobility import ROOT,PROJECT,LIVE,readzip,zipbytes
from lobby_boundary_gate import stopped
sys.path.insert(0,str(ROOT/'arena-editor'))
import editor
STAGE=ROOT/'dev/yacht-boundary-policy'
ARENAS={'underwater_base':('UnderwaterBase',19),'klut27':('Klut27',20),'middle_ages':('MiddleAges',22)}

def patch(files):
    result=dict(files)
    for ns,(tag,id)in ARENAS.items():
        state=json.loads(files[f'data/bbe_arena/editor/{ns}.json'])
        generated=editor.exported_files(state,{'arena':ns,'tag':tag,'map_id':id})
        for part in ('kill','tp'):
            key=f'data/bbe_arena/function/{ns}/{part}.mcfunction';result[key]=generated[key]
    key='data/klut27/function/fall.mcfunction';body=files[key].decode()
    body=body.replace('unless score $gamestate CmdData matches 0..1','unless score $gamestate CmdData matches 1')
    guard='execute if score $graceperiod CmdData matches 1.. run return run function bbe_arena:klut27/tp'
    if guard not in body:
        assert 'tellraw @a' in body
        body=body.replace('tellraw @a',guard+'\nexecute unless score $graceperiod CmdData matches ..0 run return 0\ntellraw @a',1)
    result[key]=body.encode()
    return result

def stage():
    STAGE.mkdir(parents=True,exist_ok=True);manifest=[]
    for i,w in enumerate((PROJECT,LIVE)):
        path=w/'datapacks/mcm.zip';before=readzip(path);after=patch(before)
        changes=[n for n in after if after[n]!=before.get(n)];assert len(changes)==7,changes
        (STAGE/f'{i}-mcm.zip').write_bytes(zipbytes(after))
        manifest.append({'world':str(w),'before':hashlib.sha256(path.read_bytes()).hexdigest(),'changes':changes})
        if i==0:
            for name in changes:
                p=ROOT/'yacht-boundary-policy/datapack'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(after[name])
    (STAGE/'stage.json').write_text(json.dumps(manifest,indent=2));print('Staged 7 functions per world; all boundaries and spawns unchanged.')

def install():
    records=json.loads((STAGE/'stage.json').read_text());backup=ROOT/'.minecraft/backups/yacht-boundary-policy'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    with ExitStack()as stack:
        for record in records:stack.enter_context(stopped(Path(record['world'])))
        backup.mkdir(parents=True)
        for i,r in enumerate(records):
            w=Path(r['world']);p=w/'datapacks/mcm.zip';assert hashlib.sha256(p.read_bytes()).hexdigest()==r['before']
            archive=backup/f'{i}-world.zip'
            with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1)as z:
                for f in w.rglob('*'):
                    if f.is_file()and f.name!='session.lock':z.write(f,w.name+'/'+f.relative_to(w).as_posix())
            with zipfile.ZipFile(archive)as z:assert z.testzip()is None
            r['backup']=str(archive);r['backup_sha256']=hashlib.sha256(archive.read_bytes()).hexdigest()
            print('Verified full backup:',archive,flush=True)
        for i,r in enumerate(records):
            w=Path(r['world']);p=w/'datapacks/mcm.zip';assert hashlib.sha256(p.read_bytes()).hexdigest()==r['before']
            before=readzip(p);after=readzip(STAGE/f'{i}-mcm.zip')
            assert before.keys()==after.keys();assert sorted(n for n in before if before[n]!=after[n])==sorted(r['changes'])
            raw=(STAGE/f'{i}-mcm.zip').read_bytes();temp=p.with_name('mcm.zip.policy-pending');temp.write_bytes(raw);temp.replace(p);assert p.read_bytes()==raw
            with zipfile.ZipFile(r['backup'])as z:
                for name in z.namelist():
                    rel=Path(name).relative_to(w.name)
                    if rel.as_posix()!='datapacks/mcm.zip':assert (w/rel).read_bytes()==z.read(name)
            r['after']=hashlib.sha256(raw).hexdigest()
    (backup/'installation.json').write_text(json.dumps(records,indent=2)+'\n');(STAGE/'installed.json').write_text(json.dumps(records,indent=2)+'\n')
    print('Installed both integrated worlds. All other save files preserved.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--install',action='store_true');args=parser.parse_args()
    install()if args.install else stage()
