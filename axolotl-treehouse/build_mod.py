#!/usr/bin/env python3
"""Compile the three-block visual backport with the pack's pinned Java and NeoForge."""
import hashlib,json,os,subprocess,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=Path(__file__).resolve().parent
runtime=ROOT/'dev/launcher'
lib=runtime/'libraries/net/neoforged/neoforge/21.4.158'
priority=[lib/f'neoforge-21.4.158-{kind}.jar'for kind in ['client','universal']]
jars=priority+sorted(p for p in(runtime/'libraries').rglob('*.jar')if p not in priority)
metadata='''modLoader="javafml"
loaderVersion="[4,)"
license="All Rights Reserved"
[[mods]]
modId="backstabbed_treehouse"
version="1.0.0"
displayName="Backstabbed Treehouse Blocks"
description="Visual-only spruce shelf, firefly bush and cactus flower backports. Required on both client and server."
[[dependencies.backstabbed_treehouse]]
modId="neoforge"
type="required"
versionRange="[21.4.158,21.5)"
side="BOTH"
[[dependencies.backstabbed_treehouse]]
modId="minecraft"
type="required"
versionRange="[1.21.4]"
side="BOTH"
'''
with tempfile.TemporaryDirectory()as tmp:
 classes=Path(tmp)
 sources=sorted((BASE/'src').rglob('*.java'))
 subprocess.run([str(runtime/'jvm/java-runtime-delta/bin/javac'),'--release','21','-proc:none','-classpath',os.pathsep.join(map(str,jars)),'-d',str(classes),*map(str,sources)],check=True)
 entries={'META-INF/neoforge.mods.toml':metadata.encode()}
 entries.update({p.relative_to(classes).as_posix():p.read_bytes()for p in classes.rglob('*.class')})
 entries.update({p.relative_to(BASE/'resources').as_posix():p.read_bytes()for p in(BASE/'resources').rglob('*')if p.is_file()})
 entries['treehouse-build.json']=json.dumps({'sources':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sources},'assets':json.loads((BASE/'assets-provenance.json').read_text())},sort_keys=True).encode()
 output=ROOT/'.minecraft/mods/backstabbed-treehouse-1.0.0.jar'
 with zipfile.ZipFile(output.with_suffix('.pending'),'w',compression=zipfile.ZIP_DEFLATED)as z:
  for name,data in sorted(entries.items()):
   info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.external_attr=0o100644<<16;z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED)
 output.with_suffix('.pending').replace(output)
 print(output)
