// Coordinates identify inclusive block cells; a one-block selection measures 1 × 1 × 1.
export function fullBounds(size) {
  return { min: [0, 0, 0], max: size.map(value => value - 1) }
}

export function boundsFromPoints(points, fallback) {
  if (!points.length) return { min: [...fallback.min], max: [...fallback.max] }
  return {
    min: [0, 1, 2].map(axis => Math.min(...points.map(point => point[axis]))),
    max: [0, 1, 2].map(axis => Math.max(...points.map(point => point[axis]))),
  }
}

export function contains(bounds, point) {
  return point.every((value, axis) => value >= bounds.min[axis] && value <= bounds.max[axis])
}

export function measure(bounds) {
  const size = bounds.max.map((value, axis) => value - bounds.min[axis] + 1)
  return { size, footprint: size[0] * size[2], volume: size[0] * size[1] * size[2], diagonal: Math.hypot(...size) }
}

export function toWorld(point, origin) {
  return point.map((value, axis) => value + origin[axis])
}

// Amanatides/Woo voxel traversal: O(cells crossed), independent of mesh complexity.
// Return the first occupied, visible cell, or null if the ray misses the build.
export function pickVoxel(rayOrigin, rayDirection, size, occupied) {
  let near = 0, far = Infinity
  for (let axis = 0; axis < 3; axis++) {
    if (Math.abs(rayDirection[axis]) < 1e-12) {
      if (rayOrigin[axis] < 0 || rayOrigin[axis] >= size[axis]) return null
      continue
    }
    const a = -rayOrigin[axis] / rayDirection[axis]
    const b = (size[axis] - rayOrigin[axis]) / rayDirection[axis]
    near = Math.max(near, Math.min(a, b))
    far = Math.min(far, Math.max(a, b))
  }
  if (near > far || !Number.isFinite(far)) return null
  const entry = rayOrigin.map((value, axis) => value + rayDirection[axis] * (near + 1e-7))
  const cell = entry.map(value => Math.floor(value))
  const step = rayDirection.map(value => Math.sign(value))
  const delta = rayDirection.map(value => value ? Math.abs(1 / value) : Infinity)
  const next = cell.map((value, axis) => !step[axis] ? Infinity :
    ((step[axis] > 0 ? value + 1 : value) - rayOrigin[axis]) / rayDirection[axis])
  for (let count = 0; count < size.reduce((a, b) => a + b, 0) + 3; count++) {
    if (cell.some((value, axis) => value < 0 || value >= size[axis])) return null
    if (occupied(cell)) return [...cell]
    const t = Math.min(...next)
    if (t > far) return null
    // Advance all tied axes so exact edge/corner crossings do not select adjacent cells.
    for (let axis = 0; axis < 3; axis++) if (next[axis] <= t + 1e-10) {
      cell[axis] += step[axis]
      next[axis] += delta[axis]
    }
  }
  return null
}
