// User-authorized substitutions for Java 1.21.4, expressed as sparse structures.
// Run with the installed minecraft-builder-skill; KAIZEN_ARENA selects the map.
import fs from 'node:fs'

export default function build(api) {
  const arena = process.env.KAIZEN_ARENA || 'meridian_base'
  if (!['meridian_base', 'underwater_base'].includes(arena)) throw Error('Unknown arena')
  const manifest = JSON.parse(fs.readFileSync(new URL(`../../docs/arenas/${arena}_compatibility.json`, import.meta.url)))
  const structure = api.createStructure(manifest.size)
  for (const block of manifest.changes) {
    api.setBlock(structure, block.position.map((v, a) => v - manifest.origin[a]),
      block.after.Name, block.after.Properties,
      block.after.Name === 'minecraft:skeleton_skull' ? api.createBlockNbt({ id: 'minecraft:skull' }) : undefined)
  }
  return { structure, metadata: { name: `${arena}-compatibility`, origin: manifest.origin,
    creator: 'KAIZEN87; compatibility substitutions authorized by the user',
    description: 'Sparse decoration substitutions only; no architecture or routes changed.' } }
}
