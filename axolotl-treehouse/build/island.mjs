import fs from 'node:fs';
const treeReference=JSON.parse(fs.readFileSync(new URL('./central-tree-reference.json',import.meta.url)));
const sourceGround=JSON.parse(fs.readFileSync(new URL('./source-ground.json',import.meta.url)));
// Heuristic landscape reconstruction from the user's video screenshot.
// The original treehouse is overlaid separately at [-17,73,-18] and is never regenerated.
export default function build(api) {
 const s=api.createStructure([128,112,128]), cells=new Map(), heights=new Map();
 const key=(x,y,z)=>`${x},${y},${z}`;
 const put=(x,y,z,b)=>{x=Math.round(x);y=Math.round(y);z=Math.round(z);cells.set(key(x,y,z),[x,y,z,b]);};
 const box=(a,b,block)=>{for(let x=a[0];x<=b[0];x++)for(let y=a[1];y<=b[1];y++)for(let z=a[2];z<=b[2];z++)put(x,y,z,block);};
 const rnd=(x,z)=>{const n=Math.sin(x*127.1+z*311.7)*43758.5453;return n-Math.floor(n)};
 const radius=a=>48+3*Math.sin(3*a+.5)+2*Math.cos(5*a)+1.6*Math.sin(9*a);
 const hill=(x,z,cx,cz,r,h)=>Math.max(0,1-Math.hypot(x-cx,z-cz)/r)*h;
 // Irregular, steep banks replace the beach disk. Broken stone bands continue below water.
 for(let x=-57;x<=57;x++)for(let z=-57;z<=57;z++){
  const d=radius(Math.atan2(z/0.93,x))-Math.hypot(x,z/0.93);if(d<=0)continue;
  let h=73+hill(x,z,-28,-20,19,15)+hill(x,z,28,-20,18,7)+hill(x,z,3,-35,14,5)+hill(x,z,29,23,15,3);
  if(d<5)h-=Math.max(0,4-d)*1.3;
  const sx=Math.max(-17,Math.min(16,x)),sz=Math.max(-18,Math.min(18,z));
  const edgeDistance=Math.max(Math.abs(x-sx),Math.abs(z-sz));
  if(edgeDistance===0)h=73;
  else if(edgeDistance<7&&sourceGround[`${sx},${sz}`]!==undefined){
   const t=Math.max(0,(edgeDistance-1)/6);h=sourceGround[`${sx},${sz}`]*(1-t)+h*t;
  }
  h=Math.floor(h);heights.set(`${x},${z}`,h);
  for(let y=57;y<=h;y++){
   const surface=y===h;
   const rock=rnd(x+Math.floor(y/3)*3,z+Math.floor(y/4)*7);
   let block=surface?'grass_block':y>h-3?'dirt':rock<.12?'mossy_cobblestone':rock<.3?'andesite':rock<.43?'cobblestone':'stone';
   if(surface&&d<2&&rnd(x,z)>.48)block=rock>.5?'stone':'mossy_cobblestone';
   put(x,y,z,block);
  }
  if(d<3&&rnd(x,z)>.83)for(let y=h-1;y>Math.max(64,h-7);y--)put(x-1,y,z,'vine[east=true,north=false,south=false,west=false,up=false]');
 }
 const ground=(x,z)=>heights.get(`${Math.round(x)},${Math.round(z)}`);
 const clear=(x,y,z)=>put(x,y,z,'air');
 // Large walk-through stone arch beneath the raised rear bluff, as in the video.
 for(let x=-54;x<=-20;x++)for(let z=-27;z<=-13;z++)for(let y=73;y<=84;y++){
  if(((z+20)/6)**2+((y-76)/8)**2<1&&y>=73)clear(x,y,z);
 }
 // Follow the terrain with varied three-wide paths instead of concentric rings.
 const path=(points,width=1)=>{
  for(let j=0;j<points.length-1;j++){
   const a=points[j],b=points[j+1],n=Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])*2);
   for(let i=0;i<=n;i++){
    const x=Math.round(a[0]+(b[0]-a[0])*i/n),z=Math.round(a[1]+(b[1]-a[1])*i/n);
    for(let dx=-width;dx<=width;dx++)for(let dz=-width;dz<=width;dz++){
     const xx=x+dx,zz=z+dz,h=ground(xx,zz);if(h===undefined)continue;
     put(xx,h,zz,rnd(xx,zz)>.86?'gravel':rnd(xx,zz)>.45?'coarse_dirt':'dirt_path');
    }
   }
  }
 };
 path([[-19,-9],[-26,-12],[-32,-24],[-23,-34],[-8,-30],[8,-28],[18,-20]]);
 path([[-19,8],[-28,11],[-31,22],[-21,30],[-6,30],[8,32],[24,27],[31,13],[25,3],[18,1]]);
 path([[-27,11],[-36,8],[-41,14],[-44,25]]);
 path([[-15,21],[-18,29],[-28,36],[-34,33]]);
 path([[18,-18],[23,-28],[30,-30],[35,-17],[31,0],[24,5]]);
 // Long, broken stone retaining walls follow the cliff, with moss and recessed bays.
 for(const z of [31,34])for(let x=-32;x<=8;x++){
  const h=ground(x,z);if(h===undefined||rnd(x,z)<.15)continue;
  for(let y=h-5;y<=h;y++)if(rnd(x+y,z)>.08)put(x,y,z,rnd(x,z+y)>.4?'stone_bricks':'mossy_stone_bricks');
  if(x%7===0)put(x,h+1,z,'mossy_cobblestone_wall');
 }
 for(let z=-8;z<=16;z++){
  const x=-42,h=ground(x,z);if(h===undefined)continue;
  for(let y=h-5;y<h;y++)put(x,y,z,rnd(y,z)>.35?'mossy_stone_bricks':'stone_bricks');
 }
 // Boulders are clustered near exposed banks rather than repeated evenly along a ring.
 for(const [cx,cz]of [[-42,-4],[-35,31],[20,35],[39,-7],[-18,-37]]){
  const h=ground(cx,cz);if(h===undefined)continue;
  for(let dx=-2;dx<=2;dx++)for(let dz=-2;dz<=2;dz++)if(dx*dx+dz*dz<6){
   put(cx+dx,h,cz+dz,'stone');if(dx*dx+dz*dz<3)put(cx+dx,h+1,cz+dz,'mossy_cobblestone');
  }
 }
 const wood='spruce_planks',log='oak_log[axis=y]';
 // A sheltered quay is attached to the island. Stairs descend from the grass to lake level.
 // Keep all dock boards above lake level and include them in the actual playable footprint.
 for(let i=0;i<10;i++)for(let z=18;z<=22;z++){
  for(let y=74-i;y<=86;y++)clear(-37-i,y,z);
  put(-37-i,73-i,z,'spruce_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]');
 }
 box([-51,64,15],[-45,64,28],wood);box([-55,64,24],[-45,64,28],wood);
 for(const x of [-51,-45,-55])for(const z of [15,28]){
  if(x===-55&&z===15)continue;
  box([x,59,z],[x,66,z],log);put(x,67,z,'lantern[hanging=false]');
 }
 for(let z=17;z<=25;z+=3){put(-51,65,z,'spruce_fence');put(-45,65,z,'spruce_fence');}
 for(const [x,z]of [[-49,26],[-46,16]]){put(x,65,z,'barrel[facing=up,open=false]');put(x,66,z,'potted_fern');}
 // Raised timber pavilion on the front cliff, connected to a winding garden path.
 const pavilion=(x,z,y)=>{
  box([x-4,y,z-3],[x+4,y,z+3],wood);
  for(const dx of [-4,4])for(const dz of [-3,3])box([x+dx,y-4,z+dz],[x+dx,y+5,z+dz],log);
  for(const dx of [-4,0,4])box([x+dx,y+4,z-4],[x+dx,y+4,z+4],'spruce_slab[type=bottom,waterlogged=false]');
  for(const dz of [-3,3])box([x-5,y+4,z+dz],[x+5,y+4,z+dz],'spruce_slab[type=bottom,waterlogged=false]');
  for(let dz=-2;dz<=2;dz++){put(x-4,y+1,z+dz,'spruce_fence');put(x+4,y+1,z+dz,'spruce_fence');}
  put(x,y+3,z,'lantern[hanging=true]');
 };
 pavilion(-20,35,75);
 for(let i=0;i<3;i++)box([-22,74-i,31-i],[-18,74-i,31-i],'spruce_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]');
 // A little stone arch and ruined retaining wall border the west garden.
 for(let z=1;z<=9;z++){
  const y=ground(-32,z)??73;put(-32,y+1,z,'mossy_stone_bricks');
  if(z<3||z>7)box([-32,y+2,z],[-32,y+4,z],'mossy_stone_bricks');
 }
 box([-32,78,3],[-32,78,7],'mossy_stone_brick_slab[type=bottom,waterlogged=false]');
 // Two golden wheat patches, with embedded irrigation and irregular edges.
 for(const [cx,cz,rx,rz]of [[-5,36,8,5],[34,3,5,8]])for(let dx=-rx;dx<=rx;dx++)for(let dz=-rz;dz<=rz;dz++){
  if(dx*dx/(rx*rx)+dz*dz/(rz*rz)>1||rnd(cx+dx,cz+dz)<.09)continue;
  const x=cx+dx,z=cz+dz,h=ground(x,z);if(h===undefined)continue;
  put(x,h,z,dx===0&&dz===0?'water[level=0]':'farmland[moisture=7]');
  if(dx!==0||dz!==0)put(x,h+1,z,'wheat[age=7]');
 }
 // Each island tree is a scaled/rotated sample of the original central tree,
 // including its azalea canopies, oak-wood elbows, spruce twigs and glow vines.
 const stateString=state=>state.Name.replace('minecraft:','')+(state.Properties?'['+Object.entries(state.Properties).map(([k,v])=>`${k}=${v}`).join(',')+']':'');
 const rotate=(x,z,q)=>q===0?[x,z]:q===1?[-z,x]:q===2?[-x,-z]:[z,-x];
 const trees=[[-29,-25,.62,0,4],[-10,-34,.55,2,5],[-33,17,.64,1,5],[3,34,.65,3,7],[-27,31,.48,0,5],[32,8,.64,2,5]];
 for(const [x,z,scale,turn,trunk]of trees){
  const y=ground(x,z);if(y===undefined)continue;
  for(let h=1;h<=trunk;h++){
   put(x,y+h,z,h%3===0?'oak_wood[axis=y]':'oak_log[axis=y]');
   if(h<trunk-1&&h%2===0)put(x+1,y+h,z,'oak_wood[axis=y]');
  }
  // Place wood/twigs before leaves so collisions in downsampling keep leafy tips.
  for(const row of treeReference.blocks){
   let [dx,dy,dz,state]=row;const [rx,rz]=rotate(Math.round(dx*scale),Math.round(dz*scale),turn);
   const props={...(state.Properties||{})};
   if(props.facing&&['north','east','south','west'].includes(props.facing))props.facing=['north','east','south','west'][(['north','east','south','west'].indexOf(props.facing)+turn)%4];
   if(turn%2&&['x','z'].includes(props.axis))props.axis=props.axis==='x'?'z':'x';
   if(state.Name.endsWith('_leaves')){props.persistent='true';props.distance='1';}
   const yy=y+trunk+Math.round(dy*scale);
   // Never let a sample's lower hanging vine overwrite the ground or a path.
   if(yy>y)put(x+rx,yy,z+rz,stateString({...state,Properties:props}));
  }
  if(trunk>=5){
   const woody=treeReference.blocks.filter(v=>v[3].Name.includes('oak_')&&v[1]>=2&&v[1]<=8);
   const anchor=woody.reduce((a,b)=>(Math.abs(a[0])+Math.abs(a[2]))>(Math.abs(b[0])+Math.abs(b[2]))?a:b);
   const [sx,sz]=rotate(Math.round(anchor[0]*scale),Math.round(anchor[2]*scale),turn),seat=y+2,beam=y+trunk+Math.round(anchor[1]*scale);
   box([x+sx-1,beam,z+sz],[x+sx+1,beam,z+sz],'spruce_fence');
   for(const dx of [-1,1])for(let yy=seat+1;yy<beam;yy++)put(x+sx+dx,yy,z+sz,'chain[axis=y,waterlogged=false]');
   box([x+sx-1,seat,z+sz],[x+sx+1,seat,z+sz],'spruce_slab[type=bottom,waterlogged=false]');
  }
 }
 // Shrubs, small flowers and hidden lanterns cluster along paths and cliff ledges.
 for(let x=-44;x<=44;x++)for(let z=-41;z<=41;z++){
  if(Math.abs(x)<20&&Math.abs(z)<22)continue;
  const h=ground(x,z);if(h===undefined)continue;
  const p=cells.get(key(x,h,z));if(!p||p[3]!=='grass_block'||cells.has(key(x,h+1,z)))continue;
  const n=rnd(x,z);
  if(n>.982){put(x,h+1,z,'flowering_azalea');if(rnd(z,x)>.5)put(x,h+2,z,'lantern[hanging=false]');}
  else if(n>.88)put(x,h+1,z,['short_grass','azure_bluet','oxeye_daisy','allium','pink_petals[flower_amount=4,facing=north]','fern'][Math.floor(rnd(z,x)*6)]);
 }
 // Small visual fireflies remain a part of the original schematic, supplied by the visual mod.
 for(const [x,y,z,b]of cells.values()){
  if(x<-64||x>63||z<-64||z>63||y<48||y>159)throw Error(`Out of landscape bounds ${x},${y},${z}`);
  api.setBlock(s,[x+64,y-48,z+64],'minecraft:'+(b==='grass_block'?'grass_block[snowy=false]':b));
 }
 return {structure:s,metadata:{name:'treehouse-island'}};
}
