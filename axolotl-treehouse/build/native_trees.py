"""Retain native tree geometry while the terrain beneath it is graded."""
import numpy as np
from scipy.ndimage import label
from scipy.spatial import cKDTree


def extract(grid, palette):
    names = [p['Name'].split(':')[1] for p in palette]
    wood = np.asarray([v.endswith(('_log', '_wood')) for v in names])[grid]
    groups, count = label(wood, structure=np.ones((3, 3, 3)))
    logs = np.argwhere(wood)
    log_groups = groups[tuple(logs.T)]
    tree_material = np.asarray([v.endswith(('_log', '_wood', '_leaves')) or v == 'bee_nest' for v in names])
    positions = np.argwhere(tree_material[grid])
    states = grid[tuple(positions.T)].copy()
    _, nearest = cKDTree(logs).query(positions, workers=4)
    owners = log_groups[nearest]
    roots = np.zeros((count + 1, 3), dtype=np.int32)
    for group in range(1, count + 1):
        members = logs[log_groups == group]
        lowest = members[members[:, 0] == members[:, 0].min()]
        roots[group] = lowest[len(lowest) // 2]
    grid[tuple(positions.T)] = 0
    return positions, states, owners, roots


def restore(grid, trees, heights, ridge_changed):
    positions, states, owners, roots = trees
    placed = []
    # The second pass translates the same native donor trees along with its ridge.
    for dx, dz in [(0, 0), (-112, 336)]:
        shifts = np.zeros(len(roots), dtype=np.int32)
        valid = np.zeros(len(roots), dtype=bool)
        for group, (y, z, x) in enumerate(roots[1:], 1):
            xx, zz = int(x + dx), int(z + dz)
            if not (0 <= xx < 512 and 0 <= zz < 512):
                continue
            if dx and not (272 <= x < 432 and 48 <= z < 176 and ridge_changed[zz, xx]):
                continue
            if not dx and ridge_changed[zz, xx]:
                continue
            if heights[zz, xx] < 64:
                continue
            shifts[group] = int(heights[zz, xx]) - (int(y) + 47)
            valid[group] = True
        take = valid[owners]
        points = positions[take].copy()
        point_states = states[take]
        point_owners = owners[take]
        points[:, 0] += shifts[point_owners]
        points[:, 1] += dz
        points[:, 2] += dx
        inside = np.all((points >= 0) & (points < np.array(grid.shape)), axis=1)
        points, point_states, point_owners = points[inside], point_states[inside], point_owners[inside]
        # Keep native rock exposed where the upslope side meets a broad canopy.
        air = grid[tuple(points.T)] == 0
        grid[tuple(points[air].T)] = point_states[air]
        for group in np.unique(point_owners):
            member = point_owners == group
            placed.append({'root': [int(roots[group, 2] + dx), int(heights[roots[group, 1] + dz, roots[group, 2] + dx]) + 1, int(roots[group, 1] + dz)],
                           'translation': [dx, int(shifts[group]), dz],
                           'positions': points[member], 'states': point_states[member]})
    return placed
