#!/usr/bin/env python3
"""Select supported, spaced Cube Block spawn contacts from the saved exterior.

Print the proposed manifest records; this tool never edits the world. Gravity
points into the supporting face, opposite its outward normal.
"""
from collections import deque
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from world_geometry import World

WORLD = ROOT / '.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies'
CLEAR = {'minecraft:' + name for name in (
    'air', 'cave_air', 'void_air', 'azure_bluet', 'cornflower', 'dandelion',
    'dead_bush', 'fern', 'oxeye_daisy', 'poppy', 'short_grass', 'vine')}
SUPPORT = {'minecraft:' + name for name in (
    'coarse_dirt', 'cobblestone', 'dirt', 'grass_block', 'gravel', 'oak_planks',
    'podzol', 'sand', 'sandstone', 'snow_block', 'spruce_planks', 'stone',
    'stone_bricks', 'jungle_leaves', 'oak_leaves', 'birch_leaves', 'spruce_leaves',
    'oak_log', 'spruce_log', 'coal_ore', 'iron_ore', 'diorite')}
# Face, normal axis/sign, outside-to-inside scan, tangent ranges, count.
FACES = (
    ('top', 1, 1, range(103, 85, -1), ((49184, 49218), (49199, 49233)), 6),
    ('bottom', 1, -1, range(38, 48), ((49184, 49218), (49199, 49233)), 6),
    ('west', 0, -1, range(49175, 49182), ((50, 84), (49199, 49233)), 5),
    ('east', 0, 1, range(49234, 49219, -1), ((50, 84), (49199, 49233)), 5),
    ('north', 2, -1, range(49163, 49197), ((49184, 49218), (50, 84)), 5),
    ('south', 2, 1, range(49250, 49234, -1), ((49184, 49218), (50, 84)), 5),
)
GRAVITY = {(0, 1): 'west', (0, -1): 'east', (1, 1): 'down',
           (1, -1): 'up', (2, 1): 'north', (2, -1): 'south'}


def face_surface(world, axis, sign, scan, tangents):
    """Only first exterior contacts qualify; never look through an obstacle."""
    nodes = set()
    for a in range(*tangents[0]):
        for b in range(*tangents[1]):
            for n in scan:
                point = [a, b]
                point.insert(axis, n)
                if world.block(*point)['Name'] in CLEAR:
                    continue
                if world.block(*point)['Name'] in SUPPORT:
                    clear = True
                    for distance in (1, 2):
                        outside = point.copy()
                        outside[axis] += sign * distance
                        clear &= world.block(*outside)['Name'] in CLEAR
                    if clear:
                        nodes.add(tuple(point))
                break
    return nodes


def neighbours(world, point, nodes, axis, sign):
    for tangent in set(range(3)) - {axis}:
        for step in (-1, 1):
            for height in (-1, 0, 1):
                other = list(point)
                other[tangent] += step
                other[axis] += sign * height
                other = tuple(other)
                if other not in nodes:
                    continue
                # Stepping up needs extra headroom at the lower contact.
                lower = list(point if height > 0 else other)
                lower[axis] += 3 * sign
                if height and world.block(*lower)['Name'] not in CLEAR:
                    continue
                yield other


def largest_surface(world, nodes, axis, sign):
    remaining, largest = set(nodes), set()
    while remaining:
        seed = min(remaining)
        seen, pending = {seed}, deque([seed])
        remaining.remove(seed)
        while pending:
            for other in neighbours(world, pending.popleft(), nodes, axis, sign):
                if other in remaining:
                    remaining.remove(other)
                    seen.add(other)
                    pending.append(other)
        if len(seen) > len(largest):
            largest = seen
    return largest


def generate(world):
    records, sizes = [], {}
    for face, axis, sign, scan, tangents, count in FACES:
        nodes = face_surface(world, axis, sign, scan, tangents)
        connected = largest_surface(world, nodes, axis, sign)
        sizes[face] = len(connected)
        candidates = {p for p in connected
                      if len(list(neighbours(world, p, connected, axis, sign))) >= 3}
        def feet(support):
            position = [v + .5 for v in support]
            position[axis] = support[axis] + (1 if sign > 0 else 0)
            # Gravity Changer shifts positive-axis body boxes by 1e-6 into
            # the support. Leave a small contact gap for sideways/up spawns.
            if face != 'top':
                position[axis] += sign * .001
            return position
        candidates = {p for p in candidates
                      if all(math.dist(feet(p), r['position']) >= 6 for r in records)}
        if len(candidates) < count:
            raise ValueError(f'{face}: insufficient supported exterior contacts')
        # Retain the validated grace-return contact on top. Other faces start
        # near their centre, then greedily maximize distance in the face plane.
        centre = [(lo + hi - 1) / 2 for lo, hi in tangents]
        tangent_axes = [a for a in range(3) if a != axis]
        def distance(p, q):
            return sum((p[a] - q[a]) ** 2 for a in tangent_axes)
        seed = (49196, 87, 49202) if face == 'top' else min(
            candidates, key=lambda p: (sum((p[a] - c) ** 2
                                           for a, c in zip(tangent_axes, centre)), p))
        assert seed in candidates
        selected = [seed]
        while len(selected) < count:
            selected.append(max(candidates - set(selected),
                                key=lambda p: (min(distance(p, q) for q in selected), p)))
        for support in selected:
            position = feet(support)
            normal = [0, 0, 0]
            normal[axis] = sign
            records.append({'face': face, 'position': position, 'support': list(support),
                            'normal': normal, 'gravity_direction': GRAVITY[axis, sign]})
    return records, sizes


if __name__ == '__main__':
    records, sizes = generate(World(WORLD))
    print(json.dumps({'spawns': records, 'connected_surface_nodes': sizes}, indent=2))
