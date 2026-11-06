import fs from 'node:fs';
const patch=JSON.parse(fs.readFileSync(new URL('./plant-patch.json',import.meta.url)));
export default function(api){const structure=api.createStructure([70,103,191]);for(const q of patch)api.setBlock(structure,q.pos,q.state.Name,q.state.Properties||{});return {structure,metadata:{name:'Monolith plant compatibility repair',origin:[-37,-41,-109],description:'Only authorized newer decorative plants replaced for Minecraft 1.21.4'}};}
