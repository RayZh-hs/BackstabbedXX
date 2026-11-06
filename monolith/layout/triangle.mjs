import fs from 'node:fs';
const input = JSON.parse(fs.readFileSync(new URL('../../map-previewer/maps/monoliths/triangle/blocks.json', import.meta.url)));
export default function(api) {
  const structure = api.createStructure(input.size);
  for (const [x,y,z,state] of input.blocks) {
    const s=input.palette[state];
    const tile=input.tiles[`${x},${y},${z}`];
    api.setBlock(structure,[x,y,z],s.Name,s.Properties||{},tile?api.createBlockNbt(tile):undefined);
  }
  return {structure,metadata:{name:'Monolith triangle',origin:input.origin,creator:'KAIZEN87',description:'Three intact monoliths relocated and rotated around an open triangular center.'}};
}
