import { NbtFile, Structure } from '@mattzh72/lodestone'

const invisible = new Set(['air', 'cave_air', 'void_air', 'barrier', 'light', 'structure_void'].map(name => `minecraft:${name}`))

export function readStructure(bytes) {
  const root = NbtFile.read(bytes).root
  if (!['size', 'palette', 'blocks'].every(key => root.has(key))) {
    throw Error('Expected vanilla structure NBT (size, palette, blocks). Convert worlds, .schem, or .litematic files first.')
  }
  const source = Structure.fromNbt(root), size = source.getSize()
  if (!size.every(value => Number.isSafeInteger(value) && value > 0)) throw Error('Structure dimensions must be positive integers')
  const visible = block => block && !invisible.has(block.state.getName().toString())
  const blocks = source.getBlocks().filter(visible)
  const structure = {
    getSize: () => size,
    getBlocks: () => blocks,
    getBlock: point => { const block = source.getBlock(point); return visible(block) ? block : null },
  }
  return { structure, size, blocks }
}
