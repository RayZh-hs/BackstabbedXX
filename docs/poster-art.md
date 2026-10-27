# Map poster artwork

Panda Village's original artwork, item definition, and model were restored from
the earlier Panda Village integration. Map credits: oozner; house designs and
building help: Kapanas. Its poster was generated with OpenAI built-in imagegen
on 20 October 2026.

Yacht and River Bank were generated with the built-in imagegen tool on
26 October 2026. Their final PNG textures live at:

- `.minecraft/resourcepacks/backstabbed-resource/assets/yacht/textures/posters/yacht.png`
- `.minecraft/resourcepacks/backstabbed-resource/assets/river_bank/textures/posters/river_bank.png`

The textures illustrate the map themes. They are voting artwork, not screenshots
of the playable arenas.

Meridian Base, Bagger 288 and Underwater Base were added on 27 October 2026.
Their artwork reuses KAIZEN87's original map-webpage imagery. Meridian uses the
user-supplied sunset PNG unchanged, with the large title at the bottom. Bagger
uses a modern black-ink-on-white technical drawing with a bottom title block.
Underwater uses a large right-aligned title below open water. All three use
1024 × 1536 textures and credit KAIZEN87. Exact final prompts, source image URLs,
generation/selection methods, asset paths and SHA-256 hashes are recorded in
[kaizen_posters.json](arenas/kaizen_posters.json).

## Voting-booth model placement

Panda Village, River Bank and Yacht use the original voting display's X offset
`+0.99`, 2× scale and 90° rotation. Their flat models must therefore use model
Z **0**, matching the original posters: centring the item at 8/16 moves the
rendered face one block towards the lobby, to world X **27.99**, just in front
of the X=28 terracotta backing. Using Z=8 with that offset buries the artwork
inside the backing block and leaves an apparently empty voting slot. River
Bank in slot 2 was the reported case; all three affected models were corrected.

Subway Station uses X offset `−0.01` with model Z **8**, giving the same world
face position. Its configurator explicitly preserves that geometry when copying
the Yacht model. The placement test follows each voting command through its
item definition and model, projects its face onto every applicable saved booth,
and checks that the artwork is in air immediately in front of the backing.

This repair changes resource-pack model geometry only. Existing saved display
entities work after the client reloads its resource pack (F3+T); the arena builds
and gameplay datapack require no changes.

Verification on 26 October 2026: `make test` passed all 25 tests; `make pack`
rebuilt the installed/resource-pack ZIPs and client archive. A separate graphical
Minecraft Java 1.21.4 client rendered the three repaired models at the voting
booth coordinates in a copied save. Screenshots and the client log are retained
under `map-previewer/maps/poster-repair/` (Git ignored). The running NeoForge
client's log also confirmed reloading the rebuilt pack at 20:49 local time.
The original model files, configurator, test and documentation were backed up
before editing in
`.minecraft/backups/poster-repair/before-wall-plane-fix-20261026T124720Z.zip`
(SHA-256 `88bc0b1b9833eb815af8f9fb05498eca403267d3517398b7fdf3a1ea081267f5`).

## Yacht prompt

Use case: stylized-concept. Create one finished Minecraft minigame map-voting
poster, vertical 2:3 aspect ratio, edge-to-edge artwork. Subject: an elegant large
white quartz Minecraft yacht with multiple decks and cyan glass windows,
surrounded by blue ocean and small distant tropical islands. Voxel Minecraft
architecture and detailed pixel-art travel-poster illustration; dramatic but
bright afternoon sunlight, navy blue and turquoise palette with white and warm
gold. A bold clear block-pixel title reads exactly "YACHT" at the top. Smaller
footer reads exactly "BACKSTABBED++". The boat dominates the center with a cinematic
three-quarter view. Decorative slim border. No people, no watermarks, no
purple/magenta checkerboards, no mockup, no perspective distortion of the poster
itself. This will be used as a flat 2D PNG texture in a Minecraft resource pack.

## River Bank prompt

Use case: stylized-concept. Create one finished Minecraft minigame map-voting
poster, vertical 2:3 aspect ratio, edge-to-edge artwork. Subject: a beautiful
Minecraft medieval riverside town, timber and stone houses with steep red-brown
roofs lining a winding blue river, stone bridges, green trees and grassy river
banks. Voxel Minecraft architecture and detailed pixel-art travel-poster
illustration; bright atmospheric afternoon sunlight, forest-green and blue palette
with warm cream and copper. A bold clear block-pixel title reads exactly "RIVER
BANK" at the top. Smaller footer reads exactly "BACKSTABBED++". View down the river
through the buildings and a bridge, engaging cinematic composition. Decorative
slim border. No people, no watermarks, no purple/magenta checkerboards, no mockup,
no perspective distortion of the poster itself. This will be used as a flat 2D
PNG texture in a Minecraft resource pack.

## Subway Station prompt

Generated with OpenAI built-in imagegen on 26 October 2026; inspected for title,
footer, proportions and recognisable station features. Final texture:
`.minecraft/resourcepacks/backstabbed-resource/assets/subway_station/textures/posters/subway_station.png`
(1024 × 1536). Original build: KnotXackly,
https://www.minecraftmaps.com/51929-subway-station-original-build.

Use case: stylized-concept. Asset type: finished Minecraft Backstabbed++ map-voting poster. Create one vertical 2:3 edge-to-edge PNG artwork in the established detailed pixel-art travel-poster style. Subject: KnotXackly's Subway Station, a monumental underground voxel railway hall with a long terracotta-pink granite central platform, dark wooden benches, small potted trees, slim dark stone lamp posts with square sea-lantern lights, ornate pale-gray tuff/concrete vaulted ribs and a high geometric ceiling with warm glowing froglight panels. Stationary silver-gray metro trains with cyan/teal doors and black windows flank the central platform; parallel tracks lead toward dark tunnels. Show a cinematic view down the platform, with convincing Minecraft block architecture. Cool slate-gray and teal, warm copper-pink floor and golden lights. Bold highly legible block-pixel title at top reads exactly "SUBWAY STATION", on two lines if needed. Small footer reads exactly "BACKSTABBED++". Fine decorative border matching the existing arena posters. No people, no watermarks, no extra slogans, no outdoor skyline, no checkerboards, no poster mockup or perspective distortion of the poster itself. This is thematic voting artwork for the actual station, not a screenshot.
