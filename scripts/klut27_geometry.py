"""Conservative saved-block collision and route analysis for KLUT-27."""
from collections import deque
from pathlib import Path
import json
import nbtlib as nbt

ROOT = Path(__file__).resolve().parent.parent
OFFSET = 36864
# Only full collision cubes are admitted; slabs, stairs, doors and all hazards
# are deliberately excluded as spawn support. Air is required in the body.
FULL = {'iron_block','polished_blackstone','oxidized_copper','terracotta','sea_lantern','weathered_copper','exposed_copper','gold_block','prismarine_bricks','glass','blackstone','diorite','polished_diorite','diamond_block','oxidized_cut_copper','chiseled_stone_bricks','crafting_table','target','white_shulker_box'}
SUFFIXES = ('_concrete','_terracotta','_planks','_wood','_log','_stem','_hyphae','_froglight','_stained_glass')

def read_blocks():
    structure = nbt.load(ROOT / 'map-previewer/maps/klut27/klut27.nbt')
    origin = json.loads((ROOT / 'map-previewer/maps/klut27/klut27.json').read_text())['origin']
    return {tuple(int(b['pos'][i])+origin[i] for i in range(3)): structure['palette'][int(b['state'])] for b in structure['blocks']}

def short(state):
    return str(state.get('Name','minecraft:air')).removeprefix('minecraft:')

def solid(state):
    name = short(state)
    return (name in FULL or name.endswith(SUFFIXES)) and str(state.get('Properties',{}).get('waterlogged','false')) == 'false'

def head_clear(state):
    name=short(state); props=state.get('Properties',{})
    # Wall signs have no collision. A closed top trapdoor begins at 1.8125m
    # above the feet; the standing player reaches 1.8m.
    return name=='air' or name.endswith('_wall_sign') or (name.endswith('_trapdoor') and str(props.get('half'))=='top' and str(props.get('open'))=='false' and str(props.get('waterlogged'))=='false')

def safe(blocks, pos):
    x,y,z = pos
    return solid(blocks.get((x,y-1,z),{})) and short(blocks.get((x,y,z),{}))=='air' and head_clear(blocks.get((x,y+1,z),{}))

def analyze():
    blocks = read_blocks()
    cells = {(x,y+1,z) for (x,y,z),s in blocks.items() if solid(s) and safe(blocks,(x,y+1,z)) and y >= -36}
    # Guaranteed walking edges, requiring clear overhead at both ends for steps.
    graph = {p:set() for p in cells}
    for x,y,z in cells:
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            for dy in (-1,0,1):
                q=(x+dx,y+dy,z+dz)
                if q in cells and all(head_clear(blocks.get((cx,max(y,q[1])+1,cz),{})) for cx,cz in ((x,z),(q[0],q[2]))):
                    graph[(x,y,z)].add(q)
    # Elevator links preserve the original six vertical routes, only accepting
    # destinations with two full air cells. Runtime checks use the same rule.
    columns={}
    for p,s in blocks.items():
        if short(s)=='white_shulker_box':
            x,y,z=p
            if (x,y+1,z) in cells:
                columns.setdefault((x,z),[]).append((x,y+1,z))
    for values in columns.values():
        values.sort(key=lambda p:p[1])
        for a,b in zip(values,values[1:]):
            graph[a].add(b); graph[b].add(a)
    unseen=set(cells); components=[]
    while unseen:
        seed=min(unseen); component={seed}; queue=deque([seed]); unseen.remove(seed)
        while queue:
            for q in graph[queue.popleft()]:
                if q in unseen:
                    unseen.remove(q);component.add(q);queue.append(q)
        components.append(component)
    components.sort(key=len,reverse=True)
    return blocks,graph,components,columns

if __name__=='__main__':
    blocks,graph,components,columns=analyze()
    print('components',[(len(c),min(p[1] for p in c),max(p[1] for p in c)) for c in components[:20]])
    print('elevators',columns)
    for i,c in enumerate(components[:8]):
        print(i,sorted(c)[:20])
