# Backstabbed++ development

For previewing candidate Minecraft maps, measuring arena bounds, or assessing a
map for porting, use the project skill at
[.agents/skills/minecraft-map-preview/SKILL.md](.agents/skills/minecraft-map-preview/SKILL.md).
The maintained viewer is in `map-previewer/`; downloaded worlds and preview
artifacts belong in its Git-ignored `maps/` directory.

For adding or porting an arena into the game, or repairing an integration, use
[.agents/skills/backstabbed-map-creator/SKILL.md](.agents/skills/backstabbed-map-creator/SKILL.md).
Complete the build, an imagegen voting poster, validated spawns, and player
containment. Ask the user before solving a problem by altering the map's design
or geometry; once that fix is authorized, back up the map first and use
`minecraft-builder-skill` to prepare and preview the repair.

Both project skills are vendored as real files under `.agents/skills/`.
Use those local instructions even when a global skill catalog does not list
them; the preview skill's runtime is the checked-in `map-previewer/` tool.
