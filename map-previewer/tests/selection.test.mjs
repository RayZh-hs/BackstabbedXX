import { test } from 'node:test'
import assert from 'node:assert/strict'
import { boundsFromPoints, contains, fullBounds, measure, pickVoxel, toWorld } from '../viewer/selection.js'
import { parseArgs } from '../preview.mjs'

test('default box wraps every block, including both corner cells', () => {
  const box = fullBounds([70, 34, 384])
  assert.deepEqual(boundsFromPoints([], box), box)
  assert.deepEqual(measure(box).size, [70, 34, 384])
  assert.equal(measure(box).footprint, 26880)
  assert.equal(measure(box).volume, 913920)
  assert.equal(contains(box, [69, 33, 383]), true)
  assert.equal(contains(box, [70, 33, 383]), false)
})

test('corner order is independent and a single point is a one-metre box', () => {
  const points = [[8, 2, 9], [2, 7, 3]]
  const box = boundsFromPoints(points)
  assert.deepEqual(box, { min: [2, 2, 3], max: [8, 7, 9] })
  assert.deepEqual(measure(box).size, [7, 6, 7])
  assert.deepEqual(measure(boundsFromPoints([[2, 7, 3]])).size, [1, 1, 1])
  assert.deepEqual(toWorld(box.min, [-12, -60, -214]), [-10, -58, -211])
})

test('extension points grow the union, and removing an extreme shrinks it', () => {
  const corners = [[0, 0, 0], [9, 9, 9]]
  const extended = [...corners, [-5, 4, 15], [4, 3, 3]]
  assert.deepEqual(boundsFromPoints(extended), { min: [-5, 0, 0], max: [9, 9, 15] })
  assert.deepEqual(boundsFromPoints(extended.filter((_, index) => index !== 2)), boundsFromPoints(corners))
  assert.deepEqual(boundsFromPoints([...corners, [4, 3, 3]]), boundsFromPoints(corners))
  assert.deepEqual(boundsFromPoints([[9, 9, 9], [-5, 4, 15]]), { min: [-5, 4, 9], max: [9, 9, 15] })
})

test('ray picking works from both directions and from inside the build', () => {
  const occupied = point => point[0] === 4 && point[1] === 1 && point[2] === 1
  const size = [10, 4, 4]
  assert.deepEqual(pickVoxel([-4, 1.5, 1.5], [1, 0, 0], size, occupied), [4, 1, 1])
  assert.deepEqual(pickVoxel([14, 1.5, 1.5], [-1, 0, 0], size, occupied), [4, 1, 1])
  assert.deepEqual(pickVoxel([4.5, 1.5, 1.5], [0, 0, 1], size, occupied), [4, 1, 1])
  assert.equal(pickVoxel([-1, 1.5, 1.5], [-1, 0, 0], size, occupied), null)
  assert.equal(pickVoxel([-1, 8, 1.5], [1, 0, 0], size, occupied), null)
  assert.equal(pickVoxel([0, 4, 0], [1, 0, 0], size, occupied), null)
})

test('ray picking skips hidden cells and handles exact corner crossings', () => {
  const floor = point => point[1] === 0
  assert.deepEqual(pickVoxel([2.5, 10, 2.5], [0, -1, 0], [5, 5, 5], floor), [2, 0, 2])
  assert.equal(pickVoxel([2.5, 10, 2.5], [0, -1, 0], [5, 5, 5], () => false), null)
  // A ray exactly along x=y only enters cells whose x and y match.
  assert.equal(pickVoxel([-1, -1, .5], [1, 1, 0], [5, 5, 5], p => p[0] === 1 && p[1] === 0), null)
  assert.deepEqual(pickVoxel([-1, -1, .5], [1, 1, 0], [5, 5, 5], p => p[0] === 3 && p[1] === 3), [3, 3, 0])
})

test('server options accept explicit structure paths and reject invalid ports', () => {
  assert.equal(parseArgs(['--nbt', 'a.nbt', '--port', '5190']).port, 5190)
  assert.match(parseArgs(['--nbt', 'a.nbt']).metadata, /a\.json$/)
  assert.equal(parseArgs(['--open']).open, true)
  for (const args of [['--port', '0'], ['--port', '65536'], ['--port', 'abc'], ['--nbt'], ['--other']]) {
    assert.throws(() => parseArgs(args))
  }
})
