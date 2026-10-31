"""Narrow migration for editor boundaries incorrectly running during lobby state 0."""
from pathlib import Path
from contextlib import ExitStack,contextmanager
import argparse,datetime,hashlib,json,msvcrt,zipfile
from klut27_mobility import ROOT,PROJECT,LIVE,readzip,zipbytes

STAGE=ROOT/'dev/lobby-boundary'
ARENAS=('underwater_base','klut27','middle_ages')
OLD=b'execute unless score $gamestate CmdData matches 0..1 run return 0'
NEW=b'execute unless score $gamestate CmdData matches 1 run return 0'

def patch(files):
    result=dict(files)
    for arena in ARENAS:
        name=f'data/bbe_arena/function/{arena}/tick.mcfunction'
        body=files[name]
        assert body.count(OLD)==1 or body.count(NEW)==1,name
        result[name]=body.replace(OLD,NEW)
    return result

def stage():
    STAGE.mkdir(parents=True,exist_ok=True)
    originals={}
    for i,w in enumerate((PROJECT,LIVE)):
        p=w/'datapacks/mcm.zip';raw=p.read_bytes();originals[str(p)]=hashlib.sha256(raw).hexdigest()
        after=patch(readzip(p));(STAGE/f'{i}-mcm.zip').write_bytes(zipbytes(after))
        if i==0:
            for arena in ARENAS:
                name=f'data/bbe_arena/function/{arena}/tick.mcfunction'
                out=ROOT/'lobby-boundary/datapack'/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(after[name])
    (STAGE/'originals.json').write_text(json.dumps(originals,indent=2))
    print('Staged three boundary gates for each integrated save; no save changed.')

def test_pack():
    files=readzip(STAGE/'0-mcm.zip')
    for tag in ('load','tick'):files[f'data/minecraft/tags/function/{tag}.json']=b'{"values":[]}'
    # Record the real boundary's elimination call without invoking unrelated match UI.
    files['data/mcm/function/game/playerdeath.mcfunction']=b'scoreboard players add @s test_deaths 1\nscoreboard players set @s dead 1\n'
    target=ROOT.parent/'GravityChangerMod/gravity-changer-neoforge/run-klut/world/datapacks/mcm.zip'
    target.write_bytes(zipbytes(files));print('Staged patched isolated GameTest pack.')

@contextmanager
def stopped(world):
    with (world/'session.lock').open('a+b')as f:
        f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
        try:yield
        finally:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)

def install():
    originals=json.loads((STAGE/'originals.json').read_text())
    backup=ROOT/'.minecraft/backups/lobby-boundary'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    jobs=[];report={'backup':str(backup),'worlds':[]}
    with ExitStack()as stack:
        for w in (PROJECT,LIVE):stack.enter_context(stopped(w))
        for p,h in originals.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,'Save changed since staging: '+p
        backup.mkdir(parents=True)
        for i,w in enumerate((PROJECT,LIVE)):
            archive=backup/f'{i}-world.zip'
            with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1)as z:
                for p in w.rglob('*'):
                    if p.is_file()and p.name!='session.lock':z.write(p,w.name+'/'+p.relative_to(w).as_posix())
            with zipfile.ZipFile(archive)as z:assert z.testzip()is None
            p=w/'datapacks/mcm.zip';new=(STAGE/f'{i}-mcm.zip').read_bytes()
            before=readzip(p);after=readzip(STAGE/f'{i}-mcm.zip')
            changed=[n for n in after if after[n]!=before.get(n)]
            assert set(changed)=={f'data/bbe_arena/function/{a}/tick.mcfunction'for a in ARENAS}
            jobs.append((p,new))
            report['worlds'].append({'world':str(w),'archive':str(archive),'backup_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'changed_members':changed,'pack_sha256':hashlib.sha256(new).hexdigest()})
            print('Verified full backup:',archive,flush=True)
        for p,new in jobs:
            assert hashlib.sha256(p.read_bytes()).hexdigest()==originals[str(p)]
            tmp=p.with_name('mcm.zip.lobby-pending');tmp.write_bytes(new);tmp.replace(p)
            assert p.read_bytes()==new
        # Compare every pre-existing file to its backup, allowing only mcm.zip.
        for record in report['worlds']:
            w=Path(record['world'])
            with zipfile.ZipFile(record['archive'])as z:
                for name in z.namelist():
                    rel=Path(name).relative_to(w.name)
                    if rel.as_posix()!='datapacks/mcm.zip':assert (w/rel).read_bytes()==z.read(name),name
    (backup/'installation.json').write_text(json.dumps(report,indent=2)+'\n')
    (STAGE/'installed.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Installed and verified: only three tick gates changed in each save.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--test-pack',action='store_true');parser.add_argument('--install',action='store_true');a=parser.parse_args()
    if a.install:install()
    elif a.test_pack:test_pack()
    else:stage()
