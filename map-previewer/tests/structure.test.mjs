import { test } from 'node:test'
import assert from 'node:assert/strict'
import { NbtFile, Structure } from '@mattzh72/lodestone'
import { readStructure } from '../viewer/structure.js'
import { pickVoxel } from '../viewer/selection.js'

test('vanilla structure air and invisible cells do not stop picking or inflate block counts', () => {
  const source = new Structure([6, 2, 2])
  source.addBlock([0, 0, 0], 'minecraft:air')
  source.addBlock([1, 0, 0], 'minecraft:barrier')
  source.addBlock([2, 0, 0], 'minecraft:light', { level: '15' })
  source.addBlock([3, 0, 0], 'minecraft:stone')
  const { structure, size, blocks } = readStructure(source.writeNbt())
  assert.deepEqual(size, [6, 2, 2])
  assert.equal(blocks.length, 1)
  assert.equal(structure.getBlock([0, 0, 0]), null)
  assert.equal(structure.getBlock([2, 0, 0]), null)
  assert.deepEqual(pickVoxel([-2, .5, .5], [1, 0, 0], size, p => structure.getBlock(p) !== null), [3, 0, 0])
})

test('other NBT formats fail with a conversion instruction', () => {
  assert.throws(() => readStructure(NbtFile.create().write()), /Expected vanilla structure NBT/)
})
