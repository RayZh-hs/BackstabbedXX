"""Add all mcm_options controls to the blank upstairs wall, without changing terrain."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'data/mcm/function/lobby/options/ext_wall/'
FN = 'mcm:lobby/options/ext_wall/'
TAG = 'McmOptionsWall'
TOGGLE = [(0, '关闭', 'red'), (1, '开启', 'green')]
# key, title, kind, column, row, actions, note, states, dependency
PANELS = [
    ('shield', '首次10废料赠盾', 'toggle', 0, 0, [2], '杀手获得一次性盾牌', TOGGLE, False),
    ('kill_reward', '杀手击杀废料奖励', 'cycle', 0, 1, [9], '右键循环切换', [(-1,'受害者全部废料','yellow')]+[(n,f'{n} 个废料','yellow') for n in [0,2,3,5]], False),
    ('gunner_scrap', '持枪玩家存废料', 'toggle', 1, 0, [3], '允许保留和拾取废料', TOGGLE, False),
    ('craft_keep', '10废料获枪只扣8', 'toggle', 1, 1, [4], '关闭时扣除全部废料', TOGGLE, True),
    ('ammo', '每发子弹消耗废料', 'toggle', 2, 0, [5], '每次开枪消耗1个废料', TOGGLE, True),
    ('scrap_rate', '碎片刷新倍率', 'cycle', 2, 1, [13], '右键循环切换', [(50,'0.5×','yellow'),(80,'0.8×','yellow'),(100,'1×','yellow'),(150,'1.5×','yellow'),(200,'2×','yellow')], False),
    ('knife_timeout', '丢刀超时保底', 'toggle', 3, 0, [6], '超时后自动恢复飞刀', TOGGLE, False),
    ('knife_seconds', '丢刀保底时间', 'number', 3, 1, [7,8], '范围5至30秒', [(n,f'{n} 秒','yellow') for n in range(5,31)], False),
    ('global_glow', '全体存活玩家高亮', 'toggle', 4, 0, [10], '每2分钟5秒／最后20秒', TOGGLE, False),
    ('scrap_boost', '开局30秒碎片加速', 'toggle', 4, 1, [14], '刷新速率额外翻倍', TOGGLE, False),
    ('team_sight', '杀手互相透视', 'toggle', 5, 0, [11], '范围32格，仅杀手可见', TOGGLE, False),
    ('gun_glow', '掉落真枪全图透视', 'toggle', 5, 1, [12], '高亮地图中的掉落真枪', TOGGLE, False),
    ('mode', '游戏模式', 'mode', 6, 0, [15,16,17], '点击下方选择', [(0,'经典模式','green'),(1,'枪手模式','aqua'),(2,'杀手模式','red')], False),
    ('gunner_respawn', '枪手复活时间', 'respawn', 6, 1, [18,19,20,21,22], '仅枪手模式生效', [(n,f'{n} 秒','yellow') for n in [3,5,10,20,30]], False),
]
HOOKS = {
    'data/mcm/function/extensions/tick.mcfunction': 'execute unless score $wall_state temp = $gamestate CmdData run function '+FN+'refresh',
    'data/mcm/function/extensions/load.mcfunction': 'schedule function '+FN+'install 20t replace',
    'data/mcm/function/lobby/options/summon_options.mcfunction': 'execute unless data storage mcm:options init run function '+FN+'install',
    'data/mcm/function/extensions/options/sync.mcfunction': 'function '+FN+'refresh',
    'data/mcm/function/lobby/options/backend/click_interaction.mcfunction': 'execute if entity @s[tag='+TAG+'] run return run function '+FN+'click',
}


def pos(panel):
    if panel[0] == 'mode':
        return 84.5, 9.75
    return 112.5 + panel[3] * 4, 10.45 - panel[4] * 1.5


def text_x(key):
    return 26.86 if key == 'mode' else 27.86


def controls():
    result = []
    for panel in PANELS:
        key, title, kind, col, row, actions, note, states, dep = panel
        z, y = pos(panel)
        for i, action in enumerate(actions):
            width = 3.0 if len(actions) == 1 else {2:.6, 3:.85, 5:.52}[len(actions)]
            spacing = {1:0, 2:1.6, 3:1.05, 5:.6}[len(actions)]
            label = None if len(actions) == 1 else {
                'number':['[−1]','[+1]'], 'mode':['[经典]','[枪手]','[杀手]'],
                'respawn':['[3s]','[5s]','[10s]','[20s]','[30s]']}[kind][i]
            result.append(dict(key=key, action=action, x=text_x(key)+.01+width/2, y=y-.05,
                               z=z+(i-(len(actions)-1)/2)*spacing, width=width,
                               height=.85 if len(actions)==1 else .30, label=label,
                               selected=states[i][0] if kind in ('mode','respawn') else -999))
    return result


def snbt(value):
    # JSON is valid SNBT for this subset; command macros require numeric tags.
    # Entity Rotation specifically requires TAG_Float entries, unlike generic numeric components.
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('"Rotation":[90.0,0.0]', '"Rotation":[90f,0f]')


def generate():
    result = {}
    install = [
        '# Right of the original upstairs options; no terrain edits.',
        'execute in minecraft:overworld as @e[tag='+TAG+'] on passengers run kill @s',
        'execute in minecraft:overworld run kill @e[tag='+TAG+']',
        'execute in minecraft:overworld run function '+FN+'remove_reset',
    ]
    for y, title, color in [(12.25, '新机制设置', 'gold'), (11.85, '右键调整 · 与聊天菜单同步 · 对局中锁定', 'gray')]:
        data = {'Tags':['option',TAG], 'Rotation':[90.0,0.0], 'line_width':600,
                'text':snbt({'text':title,'color':color}), 'background':0}
        install.append(f'execute in minecraft:overworld run summon text_display 27.86 {y} 124.5 '+snbt(data))
    for panel in PANELS:
        key, title, kind, col, row, actions, note, states, dep = panel
        z, y = pos(panel)
        if len(actions)>1: y += .3
        data = {'Tags':[TAG,'McmWall_'+key], 'Rotation':[90.0,0.0], 'line_width':128,
                'transformation':{'scale':[.9,.9,.9]}, 'background':1073741824}
        args = {'data':data,'callback':FN+'update_'+key,'extra':{}}
        install.append(f'execute in minecraft:overworld positioned {text_x(key):.2f} {y:.2f} {z:.2f} run function mcm:lobby/options/summon_updatable_text '+snbt(args))
        update = ['scoreboard players set $wall_dependency temp 0']
        if dep:
            update.append('execute unless score $gunner_scrap GameRules matches 1 run scoreboard players set $wall_dependency temp 1')
        for value, label, color in states:
            args = {'title':title,'value':label,'color':color,'note':note}
            update.append(f'execute if score ${key} GameRules matches {value} run function '+FN+'render '+snbt(args))
        result[PREFIX+'update_'+key+'.mcfunction'] = ('\n'.join(update)+'\n').encode()
    for c in controls():
        args = {'data':{'Tags':[TAG], 'width':c['width'],'height':c['height'],'response':True},
                'callback':FN+'click', 'extra':{'action':c['action'],'enable_callback':FN+'enabled'}}
        # Preserve a readable action:<id> literal for action-coverage auditing.
        encoded = snbt(args).replace('"action":', 'action:')
        install.append(f"execute in minecraft:overworld positioned {c['x']:.3f} {c['y']:.2f} {c['z']:.2f} run function mcm:lobby/options/summon_interaction "+encoded)
        if c['label']:
            args = {'data':{'Tags':[TAG], 'Rotation':[90.0,0.0], 'line_width':100,
                            'transformation':{'scale':[.85,.85,.85]}, 'background':0},
                    'callback':FN+'button_update',
                    'extra':{'action':c['action'],'label':c['label'],'option':c['key'],'selected':c['selected']}}
            install.append(f"execute in minecraft:overworld positioned {text_x(c['key']):.2f} {c['y']:.2f} {c['z']:.2f} run function mcm:lobby/options/summon_updatable_text "+snbt(args))
    install.append('function '+FN+'refresh')
    result[PREFIX+'install.mcfunction'] = ('\n'.join(install)+'\n').encode()
    for name in ['click','click_player','apply','enabled','refresh','render','render_inner','button_update','button_render','remove_reset']:
        path = ROOT/'lobby-options-wall/datapack'/PREFIX/(name+'.mcfunction')
        result[PREFIX+name+'.mcfunction'] = path.read_bytes().replace(b'\r\n',b'\n')
    return result


def patched(members):
    result = dict(members)
    result.update(generate())
    for name, hook in HOOKS.items():
        text = result[name].decode().replace('\r\r\n','\n').replace('\r\n','\n')
        if name.endswith('/summon_options.mcfunction'):
            text = re.sub(r'# Reset button\n.*?(?=execute positioned 27\.9 10\.5 98\.0)', '# Reset button removed; the mode selector now occupies this wall.\n\n', text, flags=re.S)
        if hook not in text:
            text = hook+'\n'+text if name.endswith('/click_interaction.mcfunction') else text.rstrip()+'\n'+hook+'\n'
        result[name] = text.encode()
    return result
