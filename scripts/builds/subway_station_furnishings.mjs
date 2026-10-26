// Sparse second-floor furniture patch. Source coordinates use KnotXackly's
// station; the importer translates X/Z by +20480. No architecture is removed.
// Generate with the installed minecraft-builder-skill/scripts/run-build.mjs.
export const origin = [20474, -48, 20362]
export const size = [58, 7, 191]

export default function build(api) {
  const structure = api.createStructure(size)
  let south = false
  const position = (x, y, z) => [x + 6, y + 48, (south ? -45 - z : z) + 118]
  const facing = f => south ? ({ north: 'south', south: 'north' }[f] ?? f) : f
  const set = (x, y, z, block, props = {}, data) => {
    const properties = { ...props }
    if (properties.facing) properties.facing = facing(properties.facing)
    api.setBlock(structure, position(x, y, z), `minecraft:${block}`, properties,
      data ? api.createBlockNbt(data) : undefined)
  }
  const row = (x1, x2, y, z, block, props) => {
    for (let x = x1; x <= x2; x++) set(x, y, z, block, props)
  }
  const sign = (x, y, z, lines, color = 'white', f = 'south') => {
    const text = { messages: [...lines, '', '', '', ''].slice(0, 4).map(text => JSON.stringify({ text })),
      color, has_glowing_text: true }
    set(x, y, z, 'spruce_wall_sign', { facing: f, waterlogged: 'false' }, {
      id: 'minecraft:sign', front_text: text, back_text: text, is_waxed: true,
    })
  }
  const planter = (x, z) => {
    set(x, -48, z, 'mud_bricks')
    set(x, -47, z, 'azalea_leaves', { persistent: 'true', distance: '1', waterlogged: 'false' })
    for (const [dx, dz, f] of [[0, 1, 'south'], [0, -1, 'north'], [1, 0, 'east'], [-1, 0, 'west']])
      set(x + dx, -48, z + dz, 'dark_oak_trapdoor', { facing: f, half: 'bottom', open: 'true', powered: 'false', waterlogged: 'false' })
  }
  const bench = (x, z, f) => {
    row(x, x + 4, -48, z, 'spruce_stairs', { facing: f, half: 'bottom', shape: 'straight', waterlogged: 'false' })
    // Metal end armrests are vertical trapdoors; stair backs stay one block high.
    for (const [dx, direction] of [[-1, 'west'], [5, 'east']])
      set(x + dx, -48, z, 'iron_trapdoor', { facing: direction, half: 'bottom', open: 'true', powered: 'false', waterlogged: 'false' })
  }
  const waitingIsland = (x, z) => {
    bench(x, z - 1, 'south')
    bench(x, z + 1, 'north')
    row(x, x + 4, -48, z, 'mud_bricks')
    row(x, x + 4, -47, z, 'azalea_leaves', { persistent: 'true', distance: '1', waterlogged: 'false' })
    planter(x - 2, z)
    planter(x + 6, z)
  }
  const bin = (x, z) => {
    set(x, -48, z, 'cauldron')
  }
  const ticketMachine = (x, z, accent, title) => {
    row(x, x + 2, -48, z, 'polished_deepslate')
    for (let y = -47; y <= -46; y++) {
      set(x, y, z, accent)
      set(x + 2, y, z, accent)
    }
    set(x + 1, -47, z, 'black_concrete')
    set(x + 1, -46, z, 'cyan_glazed_terracotta', { facing: 'south' })
    set(x + 1, -47, z + 1, 'polished_blackstone_button', { face: 'wall', facing: 'south', powered: 'false' })
    row(x, x + 2, -45, z, 'smooth_stone_slab', { type: 'bottom', waterlogged: 'false' })
    const label = title === 'DRINKS' ? ['DRINKS', 'Cold drinks', 'Still / Sparkling', 'METRO / M']
      : title === 'SNACKS' ? ['SNACKS', 'Grab & go', 'For your journey', 'METRO / M']
      : [`TICKETS ${title}`, 'METRO / M', 'Single / Day pass', 'Tap to pay']
    sign(x + 1, -46, z + 1, label, 'white')
  }
  const board = (x, z) => {
    for (const dx of [0, 4]) {
      set(x + dx, -48, z, 'polished_deepslate')
      set(x + dx, -47, z, 'polished_deepslate_wall', { north: 'none', east: 'none', south: 'none', west: 'none', up: 'true', waterlogged: 'false' })
    }
    row(x, x + 4, -46, z, 'black_concrete')
    row(x, x + 4, -45, z, 'black_concrete')
    row(x, x + 4, -44, z, 'smooth_stone_slab', { type: 'bottom', waterlogged: 'false' })
    sign(x + 1, -45, z + 1, ['DEPARTURES', '01  Central', '02  Old Town', '03  Riverside'], 'yellow')
    sign(x + 3, -45, z + 1, ['PLATFORM', '1 / 2', '3 / 4', 'Trains below'], 'aqua')
    sign(x + 2, -46, z + 1, ['INFORMATION', 'Station concourse', '< Stairs   Stairs >', 'Enjoy your trip'], 'white')
    // Route map on the reverse: coloured route tiles with a station marker.
    for (let dx = 0; dx < 5; dx++) {
      set(x + dx, -46, z - 1, 'warped_button', { face: 'wall', facing: 'north', powered: 'false' })
    }
    sign(x + 2, -45, z - 1, ['METRO NETWORK', 'Central - Old Town', '| interchange |', 'Riverside - Park'], 'aqua', 'north')
  }
  const cafe = (x, z, newsstand) => {
    // Open counter with a staff access gap, shallow canopy and display shelving.
    for (let dx = 0; dx <= 7; dx++) {
      set(x + dx, -48, z, 'stripped_spruce_log', { axis: 'y' })
      set(x + dx, -47, z, 'smooth_stone_slab', { type: 'top', waterlogged: 'false' })
      set(x + dx, -48, z - 3, 'spruce_planks')
      set(x + dx, -47, z - 3, newsstand ? 'bookshelf' : 'dark_oak_planks')
      set(x + dx, -46, z - 3, newsstand ? 'bookshelf' : 'dark_oak_planks')
    }
    for (const dx of [0, 7]) {
      for (let y = -47; y <= -44; y++) set(x + dx, y, z - 3, 'spruce_fence', { waterlogged: 'false' })
    }
    for (let dx = 0; dx <= 7; dx++) for (let dz = -3; dz <= 0; dz++)
      set(x + dx, -43, z + dz, 'dark_oak_slab', { type: 'bottom', waterlogged: 'false' })
    for (const dx of [1, 3, 5]) {
      set(x + dx, -44, z - 2, 'lantern', { hanging: 'true', waterlogged: 'false' })
      sign(x + dx, -43, z + 1, [newsstand ? 'METRO NEWS' : 'TRACKSIDE', newsstand ? 'Books & papers' : 'COFFEE', newsstand ? 'Read / Rest' : 'Fresh every day', ''], 'yellow')
    }
    // A glazed pastry display or book display at one end of the counter.
    for (const dx of [4, 5, 6]) set(x + dx, -46, z, 'glass_pane', { waterlogged: 'false' })
    set(x + 1, -46, z, 'flower_pot')
    set(x + 2, -46, z, 'potted_fern')
    if (!newsstand) {
      set(x + 1, -46, z - 3, 'polished_blackstone')
      set(x + 1, -46, z - 2, 'polished_blackstone_button', { face: 'wall', facing: 'south', powered: 'false' })
      sign(x + 4, -46, z - 2, ['MENU', 'Espresso / Latte', 'Tea / Cocoa', 'Bakery'], 'white')
    } else {
      sign(x + 3, -46, z - 2, ['TODAY', 'City news', 'Maps & magazines', 'Good journeys'], 'white')
    }
  }
  const table = (x, z) => {
    set(x, -48, z, 'barrel', { facing: 'up', open: 'false' }, { id: 'minecraft:barrel' })
    for (const [dx, f] of [[-2, 'west'], [2, 'east']])
      set(x + dx, -48, z, 'spruce_stairs', { facing: f, half: 'bottom', shape: 'straight', waterlogged: 'false' })
  }
  for (const isSouth of [false, true]) {
    south = isSouth
    for (const [x, title] of [[-2, '01'], [2, '02'], [6, '03']]) ticketMachine(x, -116, 'cyan_terracotta', title)
    waitingIsland(1, -105)
    waitingIsland(39, -104)
    bench(1, -95, 'south')
    bench(39, -95, 'south')
    planter(-1, -95)
    planter(45, -95)
    bin(8, -95)
    bin(36, -95)
    board(10, -95)
    cafe(35, -111, south)
    table(11, -110)
    table(30, -112)
    // Paired refreshment cabinets beside the waiting area, with bright identity.
    ticketMachine(47, -115, 'red_terracotta', 'DRINKS')
    ticketMachine(47, -110, 'yellow_terracotta', 'SNACKS')
  }
  return { structure, metadata: { name: 'subway-station-second-floor-furnishings' } }
}
