// Sparse, user-authorized hatch repair; run with minecraft-builder-skill.
import fs from 'node:fs'

export default function build(api) {
  const manifest = JSON.parse(fs.readFileSync(new URL('../../docs/arenas/underwater_base_exits.json', import.meta.url)))
  const context = process.env.CONTAINMENT_CONTEXT === '1'
  const source = context ? JSON.parse(fs.readFileSync(new URL('../../map-previewer/maps/containment-fix/underwater_base-blocks.json', import.meta.url))) : null
  const origin = source?.origin ?? manifest.origin
  const size = source ? source.max.map((v, i) => v - origin[i] + 1) : manifest.size
  const structure = api.createStructure(size)
  if (context) for (const [x, y, z, state] of source.blocks) {
    if (['minecraft:air', 'minecraft:cave_air', 'minecraft:water', 'minecraft:bubble_column'].includes(state.Name)) continue
    api.setBlock(structure, [x, y, z].map((v, i) => v - origin[i]), state.Name, state.Properties)
  }
  for (const cell of manifest.changes) {
    // Magenta glass in the inspection context makes the invisible colliders visible.
    api.setBlock(structure, cell.position.map((v, i) => v - origin[i]), context ? 'minecraft:magenta_stained_glass' : cell.after.Name)
  }
  return { structure, metadata: { name: context ? 'underwater-exit-seals-context' : 'underwater-exit-seals',
    origin, creator: 'KAIZEN87; exit sealing authorized by the user', entry: [32970.5, 44.6, 32527.5],
    description: context ? 'Six barrier cells shown as magenta glass for inspection. In game the original hatches render as block displays.' : manifest.description } }
}
